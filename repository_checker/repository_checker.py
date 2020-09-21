import argparse
import os
import logging
import sys
import yaml
import subprocess
import scale
import re

CRED = '\033[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CEND = '\033[0m'

g_exp_files = [
        'settings.yml',
        'scale',
        'subject',
        'attachments',
        'description',
        'moulinette',
        'reference',
        'resources',
        '.gitignore',
        '.gitmodules',
        '.git',
    ]
EXTENSIONS_TO_IGNORE = ["jpeg", "jpg", "png"]
g_has_error = 0
g_found_languages = []

FNULL = open(os.devnull, 'w')

def info_message(string):
    logging.info(f"{CGREEN}INFO{CEND}   : {string}")

def warning_message(string):
    logging.warning(f"{CYELLOW}WARNING{CEND}: {string}")

def error_message(string):
    global g_has_error
    logging.error(f"{CRED}ERROR{CEND}  : {string}")
    g_has_error = 1

class Folder:
    ftype = ""
    languages = {}
    version = 0
    cwd = 0
    list_file = []
    treated_file = []

    def missing(self, string):
        error_message(f"{self.ftype}: Could not find {string}")

    def check_treated(self):
        untreated = [item for item in self.list_file if item not in self.treated_file and item.split(".")[-1] not in EXTENSIONS_TO_IGNORE]
        if len(untreated) > 0:
            warning_message(f"{self.ftype}: Untreated files: {[item for item in untreated]}")

    def check_versions(self, specified_language):
        global g_has_error
        self.languages = {k: v for k, v in sorted(self.languages.items(), key=lambda item: item[0])}
        s = f'{self.ftype:<14} | en: {CGREEN if self.version > 0 else CRED}{self.version:>3}{CEND}'
        state = 'ok'
        color = CGREEN
        for lg in g_found_languages:
            if lg == 'en':
                continue
            if lg not in self.languages:
                if specified_language == lg or specified_language == 'all':
                    color = CRED
                    state = 'error'
                else:
                    color = CYELLOW
                    state = "warning"
                s += ' | ' + f"{lg}: {color}{'0':>3}{CEND}"
                continue
            vers = self.languages[lg]
            color = CGREEN
            if vers > self.version or vers < 0:
                color = CRED
                state = "error"
            elif vers < self.version:
                if specified_language == lg or specified_language == 'all':
                    color = CRED
                    state = 'error'
                else:
                    color = CYELLOW
                    if state != 'error':
                        state = "warning"
            s += ' | ' + f"{lg}: {color}{vers:>3}{CEND}"
        if state == 'ok':
            info_message(s)
        elif state == 'warning':
            warning_message(s)
        elif state == 'error':
            error_message(s)
        return

    def get_versions(self, lg):
        if lg == 'en':
            return self.version
        else:
            return self.languages[lg]



class Subject(Folder):
    def __init__(self, cwd):
        self.languages = {}
        self.version = 0
        self.treated_file = []
        self.ftype = "Subject"
        self.list_file = os.listdir(cwd)
        self.cwd = cwd
        info_message(self.ftype)
        self.check_common()
        self.check_english()
        self.check_languages()
        self.check_treated()
        return

    def check_common(self):
        if "Makefile" not in self.list_file:
            self.missing("Makefile")
        else:
            self.treated_file.append("Makefile")
        for filename in self.list_file:
            reg = re.match("^[a-zA-Z]+.subject.(log|aux|toc|pyg|out|fdb_latexmk)$", filename)
            if reg != None:
                self.treated_file.append(filename)
        return

    def check_datetime(self, pdf, tex, lg):
        tex_mtime = os.stat(f'{self.cwd}/{tex}').st_mtime 
        pdf_mtime = os.stat(f'{self.cwd}/{pdf}').st_mtime
        #if tex_mtime - pdf_mtime < 10 and tex_mtime - pdf_mtime > 0:
        #    warning_message("Subject: en.subject.pdf might not be up to date")
        if tex_mtime - pdf_mtime > 10:
            if lg == 'en':
                self.version = -1
            else:
                self.languages[lg] = -1
            error_message(f"en.subject.pdf is not up to date")

    def check_english(self):
        if 'en.subject.pdf.version' not in self.list_file:
            self.missing("en.subject.pdf.version")
            return
        else:
            f = open(f'{self.cwd}/en.subject.pdf.version', 'r')
            self.version = int(f.read().strip())
            self.treated_file.append('en.subject.pdf.version')
            if 'en' not in g_found_languages:
                g_found_languages.append('en')
        if 'en.subject.pdf' not in self.list_file:
            self.missing("en.subject.pdf")
            self.version = -1
            return
        if 'en.subject.tex' not in self.list_file:
            self.missing("en.subject.tex")
            self.version = -1
            return
        self.check_datetime('en.subject.pdf', 'en.subject.tex', 'en')
        self.treated_file.append("en.subject.pdf")
        self.treated_file.append("en.subject.tex")

    def check_languages(self):
        for filename in self.list_file:
            match = re.match("^([a-zA-Z]+).subject.pdf.version$", filename)
            if match != None and match.group(1) != 'en':
                lg = match.group(1)
                if lg not in g_found_languages:
                    g_found_languages.append(lg)
                f = open(f'{self.cwd}/{lg}.subject.pdf.version', 'r')
                self.languages[lg] = int(f.read().strip())
                self.treated_file.append(f'{lg}.subject.pdf.version')
                if f"{lg}.subject.pdf" not in self.list_file:
                    self.missing(f"{lg}.subject.pdf")
                    self.languages[lg] = -1
                if f"{lg}.subject.tex" not in self.list_file:
                    self.missing(f"{lg}.subject.tex")
                    self.languages[lg] = -1
                self.check_datetime(f'{lg}.subject.pdf', f'{lg}.subject.tex', lg)
                self.treated_file.append(f"{lg}.subject.pdf")
                self.treated_file.append(f"{lg}.subject.tex")

class Scale(Folder):
    def __init__(self, cwd):
        self.languages = {}
        self.version = 0
        self.skills = []
        self.treated_file = []
        self.has_moulinette = False
        self.has_scale = True
        self.scale_attachments = None
        self.ftype = "Scale"
        self.list_file = os.listdir(cwd)
        self.cwd = cwd
        info_message(self.ftype)
        self.check_common()
        if self.has_scale == True:
            self.check_english()
            self.check_languages()
        if "attachments" in self.list_file:
            self.scale_attachments = Attachments(self.cwd + "/attachments", scale=True)
            self.treated_file.append("attachments")
        self.check_treated()
        return

    def check_common(self):
        ret_value = ''
        validator_check = 'common'
        if 'scale_common.yml' not in self.list_file:
            self.missing("scale_common.yml")
            return
        content = open(f'{self.cwd}/scale_common.yml')
        content_yml = yaml.load(content, Loader=yaml.FullLoader)
        if "has_scale" in content_yml and content_yml['has_scale'] == False:
            validator_check = 'noscale'
            self.has_scale = False
        ret_value = subprocess.run(f'ruby {sys.path[0]}/scale_validator.rb {self.cwd}/scale_common.yml --{validator_check}', shell=True, capture_output=True)
        if ret_value.returncode != 0:
            error_message(ret_value.stderr.decode('UTF-8').strip())
        if "uploads" in content_yml and "Moulinette" in content_yml["uploads"]:
            self.has_moulinette = True
        self.treated_file.append('scale_common.yml')

    def check_english(self):
        if 'en.scale.yml.version' not in self.list_file:
            self.missing("en.scale.yml.version")
        else:
            f = open(f'{self.cwd}/en.scale.yml.version', 'r')
            self.version = int(f.read().strip())
            self.treated_file.append('en.scale.yml.version')
            if 'en' not in g_found_languages:
                g_found_languages.append('en')
        if 'en.scale.yml' not in self.list_file:
            self.missing("en.scale.yml")
            self.version = -1
        else:
            ret_value = subprocess.run(f'ruby {sys.path[0]}/scale_validator.rb {self.cwd}/en.scale.yml',shell=True, capture_output=True)
            if ret_value.returncode != 0:
                error_message(ret_value.stderr.decode('UTF-8').strip())
                self.version = -1
            self.parse_skills()
            self.treated_file.append('en.scale.yml')
        return

    def check_languages(self):
        for filename in self.list_file:
            match = re.match("^([a-zA-Z]+).scale.yml.version$", filename)
            if match != None and match.group(1) != 'en':
                lg = match.group(1)
                f = open(f'{self.cwd}/{lg}.scale.yml.version', 'r')
                self.languages[lg] = int(f.read().strip())
                self.treated_file.append(f'{lg}.scale.yml.version')
                if lg not in g_found_languages:
                    g_found_languages.append(lg)
                if f"{lg}.scale.yml" not in self.list_file:
                    self.missing(f"{lg}.scale.yml")
                    self.languages[lg] = -1
                elif self.version == self.languages[lg]:
                    ret_value = subprocess.run(f'ruby {sys.path[0]}/scale_validator.rb {self.cwd}/{lg}.scale.yml',shell=True, capture_output=True)
                    if ret_value.returncode != 0:
                        error_message(ret_value.stderr.decode('UTF-8').strip())
                        self.languages[lg] = -1
                    if scale.compare(f'{self.cwd}/en.scale.yml', f'{self.cwd}/{lg}.scale.yml'):
                        error_message(f"{lg}.scale.yml differs from en.scale.yml")
                        self.languages[lg] = -1
                self.treated_file.append(f'{lg}.scale.yml')

    def parse_skills(self):
        content = open(self.cwd + "/en.scale.yml")
        yml = yaml.load(content, Loader=yaml.FullLoader)
        for item in yml['sections']:
            for question in item['questions']:
                for qskill in question['questions_skills']:
                    if qskill['name'] not in self.skills:
                        self.skills.append(qskill['name'])
        return

class Settings:
    cwd = 0
    skills = []
    def __init__(self, cwd):
        self.cwd = cwd
        info_message("Settings.yml")
        self.check_common()
        self.parse_skills()
        return

    def check_common(self):
        ret_value = subprocess.run(f'ruby {sys.path[0]}/scale_validator.rb {self.cwd}/settings.yml --settings',shell=True, capture_output=True)
        if ret_value.returncode != 0:
            error_message(ret_value.stderr.decode('UTF-8').strip())
        return

    def parse_skills(self):
        content = open(self.cwd + "/settings.yml")
        yml = yaml.load(content, Loader=yaml.FullLoader)
        if 'skills' not in yml:
            return
        for skill in yml['skills']:
            self.skills.append(' '.join(skill.split(' ')[:-1]))

class Attachments(Folder):
    def __init__(self, cwd, scale=False):
        self.languages = {}
        self.attachments = {}
        self.version = []
        self.skills = []
        self.treated_file = []
        self.ftype = "Attachments" if scale is False else "Scale Attachs"
        self.list_file = os.listdir(cwd)
        self.cwd = cwd
        info_message(self.ftype)
        self.versionned = self.check_if_versionned()
        if self.versionned == True:
            self.check_english()
            self.check_languages()
        self.check_treated()
        return

    def check_if_versionned(self):
        pattern = r"en\..+\.version"
        for fname in self.list_file:
            if re.match(pattern, fname) != None:
                return True
            else:
                self.treated_file.append(fname)
        return False

    def check_versions(self, specified_language):
        global g_has_error
        if self.ftype == "Attachments":
            infoval = "A/"
        else:
            infoval = "S/A/"
        index = -1
        self.languages = {k: v for k, v in sorted(self.languages.items(), key=lambda item: item[0])}
        for idx, vs in self.attachments.items():
            v = vs['en']
            index += 1
            s = f'{infoval + idx[:10]:<14} | en: {CGREEN if v > 0 else CRED}{v:>3}{CEND}'
            state = 'ok'
            for lg in g_found_languages:
                if lg == 'en':
                    continue
                if lg not in vs:
                    if specified_language == lg  or specified_language == 'all':
                        color = CRED
                        state = 'error'
                    else:
                        color = CYELLOW
                        state = "warning"
                    s += ' | ' + f"{lg}: {color}{'0':>3}{CEND}"
                    continue
                vers = vs[lg]
                color = CGREEN
                if vers > v or vers < 0:
                    color = CRED
                    state = "error"
                elif vers < v:
                    if specified_language == lg  or specified_language == 'all':
                        color = CRED
                        state = 'error'
                    else:
                        if state != 'error':
                            color = CYELLOW
                            state = "warning"
                s += ' | ' + f"{lg}: {color}{vers:>3}{CEND}"
            if state == 'ok':
                info_message(s)
            elif state == 'warning':
                warning_message(s)
            elif state == 'error':
                error_message(s)
        return

    def check_english(self):
        pattern = r"(en\..+)\.version"
        for fname in self.list_file:
            val = re.match(pattern, fname)
            if val != None:
                expected_file = val.group(1)
                self.attachments[expected_file.split('.', 1)[1]] = {}
                f = open(f'{self.cwd}/{fname}', 'r')
                vers_val = int(f.read().strip())
                self.version.append(vers_val)
                self.attachments[expected_file.split('.', 1)[1]]['en'] = vers_val
                self.treated_file.append(fname)
                if 'en' not in g_found_languages:
                    g_found_languages.append('en')
                if expected_file not in self.list_file:
                    self.missing(expected_file)
                    self.version[-1] = -1
                    return
                self.treated_file.append(expected_file)
        return

    def check_languages(self):
        pattern = r"(([a-z]+)\.(.+))\.version"
        for fname in self.list_file:
            val = re.match(pattern, fname)
            if val != None:
                expected_file = val.group(1)
                lg = val.group(2)
                file_value = val.group(3)
                if lg == 'en':
                    continue
                if 'en.' + file_value + '.version' not in self.list_file:
                    warning_message(f"{self.ftype}: Discarding {expected_file} - Missing english version")
                    continue
                f = open(f'{self.cwd}/{fname}', 'r')
                if lg not in self.languages:
                    self.languages[lg] = []
                vers_val = int(f.read().strip())
                self.attachments[file_value][lg] = vers_val
                self.languages[lg].append(vers_val)
                self.treated_file.append(fname)
                if lg not in g_found_languages:
                    g_found_languages.append(lg)
                if expected_file not in self.list_file:
                    self.missing(expected_file)
                    self.languages[lg][-1] = -1
                    return
                self.treated_file.append(expected_file)
        return

class Description(Folder):
    def __init__(self, cwd):
        self.languages = {}
        self.version = 0
        self.skills = []
        self.treated_file = []
        self.ftype = "Description"
        self.list_file = os.listdir(cwd)
        self.cwd = cwd
        info_message(self.ftype)
        self.check_english()
        self.check_languages()
        self.check_treated()
        return

    def check_english(self):
        if 'en.description.yml.version' not in self.list_file:
            self.missing("en.description.yml.version")
        else:
            f = open(f'{self.cwd}/en.description.yml.version', 'r')
            self.version = int(f.read().strip())
            self.treated_file.append('en.description.yml.version')
            if 'en' not in g_found_languages:
                g_found_languages.append('en')
        if 'en.description.yml' not in self.list_file:
            self.missing("en.description.yml")
            self.version = -1
        else:
            ret_value = subprocess.run(f'ruby {sys.path[0]}/scale_validator.rb {self.cwd}/en.description.yml --desc',shell=True, capture_output=True)
            if ret_value.returncode != 0:
                error_message(ret_value.stderr.decode('UTF-8').strip())
                self.version = -1
            self.treated_file.append('en.description.yml')
        return

    def check_languages(self):
        for filename in self.list_file:
            match = re.match("^([a-zA-Z]+).description.yml.version$", filename)
            if match != None and match.group(1) != 'en':
                lg = match.group(1)
                if lg not in g_found_languages:
                    g_found_languages.append(lg)
                f = open(f'{self.cwd}/{lg}.description.yml.version', 'r')
                self.languages[lg] = int(f.read().strip())
                self.treated_file.append(f'{lg}.description.yml.version')
                if f"{lg}.description.yml" not in self.list_file:
                    self.missing(f"{lg}.description.yml")
                    self.languages[lg] = -1
                else:
                    ret_value = subprocess.run(f'ruby {sys.path[0]}/scale_validator.rb {self.cwd}/{lg}.description.yml --desc',shell=True, capture_output=True)
                    if ret_value.returncode != 0:
                        error_message(ret_value.stderr.decode('UTF-8').strip())
                        self.languages[lg] = -1
                    self.treated_file.append(f'{lg}.description.yml')

class Moulinette:
    def __init__(self, cwd):
        self.languages = 0
        self.ftype = "Moulinette"
        info_message(self.ftype)
        if not os.path.exists(cwd):
            return error_message("No moulinette folder found when moulinette is expected by settings")
        self.list_file = os.listdir(cwd)
        self.cwd = cwd
        if len(self.list_file) == 0:
            return error_message("Moulinette folder is empty (and it shouldn't)")

class Repository:
    cwd = 0
    folder = 0
    list_files = []
    unexpected_files = []

    scale = None
    subject = None
    description = None
    moulinette = None
    settings = None
    languages = None
    attachments = None

    def skills_check(self):
        if self.scale.has_scale == False:
            return
        too_much = [item for item in self.scale.skills if item not in self.settings.skills]
        missing = [item for item in self.settings.skills if item not in self.scale.skills]
        if len(too_much) > 0:
            error_message(f"en Scale has {[item for item in too_much]} which isn't expected by settings")
        if len(missing) > 0:
            error_message(f"Settings expect {[item for item in missing]} which isn't in the en scale")

    def compare_versions(self, lg):
        if lg is not None and lg not in g_found_languages:
            error_message(f'Requested language "{lg.upper()}" isn\'t used on this repo')
        self.subject.check_versions(lg)
        self.scale.check_versions(lg)
        self.description.check_versions(lg)
        if self.attachments is not None and self.attachments.versionned == True:
            self.attachments.check_versions(lg)
        if self.scale.scale_attachments is not None and self.scale.scale_attachments.versionned == True:
            self.scale.scale_attachments.check_versions(lg)

    def __init__(self, cwd):
        self.folder = os.path.basename(os.path.abspath(cwd))
        self.list_files = os.listdir(cwd)
        self.cwd = cwd
        info_message(f"--- RUNNING ON {self.folder.upper()} ---")

    def check_all(self):
        self.list_unexpected()
        self.subject = Subject(self.cwd + "/subject")
        self.scale = Scale(self.cwd + "/scale")
        self.description = Description(self.cwd + "/description")
        self.settings = Settings(self.cwd)
        if self.scale.has_moulinette == True:
            self.moulinette = Moulinette(self.cwd + "/moulinette")
        if "attachments" in self.list_files:
            self.attachments = Attachments(self.cwd + "/attachments")


    def list_unexpected(self):
        return


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='which repo do you want to check?')
    parser.add_argument('path', type=str, help='repository path')
    parser.add_argument('--l', type=str, required=False, help='specific language for which you want to check translatable content (--l all for all alternative languages)')

    args = parser.parse_args()
    r = Repository(args.path)
    r.check_all()
    r.skills_check()
    r.compare_versions(None if args.l == None else args.l.lower())
    if g_has_error != 0:
        error_message(f"--- {r.folder.upper()} HAS ERRORS ---")
    else:
        info_message("--- REPOSITORY VALIDATED ---")
    sys.exit(g_has_error)