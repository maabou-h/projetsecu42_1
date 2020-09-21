* **************************************************************************** *
*                                                                              *
*               README_OR_DIE.en.txt for 42Born2peer                           *
*               Created on : Mon Oct  5 18:13:59 2015                          *
*               Made by : David "Thor" GIRON <thor@staff.42.fr>                *
*               Updated by : Catherine "Cat" MADINIER <cat@42.fr>              *
*                                                                              *
* **************************************************************************** *

I - Quick start:
----------------

  If you don't care or if you are already familiar with 42Born2Peer:

    1) Install LaTeX on your system. Check that your $PATH contains
    /usr/local/texlive/2015/bin/x86_64-darwin/

    2) Clone your 42Born2Peer repository

    3) At the root of your 42Born2Peer repository:
       $>git submodule init
       $>git submodule update
       $>git submodule foreach git pull origin master

    4) $>sudo pip install pygments (admin rights required)
    OR $>pip install --user pygments (no admin rights required)
    (Add $HOME/Library/Python/2.7/bin/ to your $PATH)

    5) cd subject && make re

    6) Enjoy
    OR Rage, read below



II - Overview of your repository
--------------------------------

  A default and clean repository for 42Born2Peer consists in 4
  folders:

  - correction/
    Sources of your fully functional implementation of the project.

  - resources/
    The submodule git@born2peer.42.fr:42born2peer/resources.git. This
    submodule provides resources and style classes for LaTeX. More on
    this below.

  - scale/
    This is where you will write your grading scale as a YAML
    description. The YOUR_PROJECT_NAME.*.yml files are self documented
    templates for your grading scale in different languages. Please
    git delete the template files you don't need and name the file(s)
    you need appropriately in order to keep this place clean. For
    instance, let's consider a project named "lube" written in
    English, you will delete the file YOUR_PROJECT_NAME.fr.yml, then
    rename the file YOUR_PROJECT_NAME.en.yml to lube.en.yml.

  - subject/
    Obviously, this is where you will write your subject. Likewise,
    you will find self documented LaTeX templates for you subject.
    Delete the templates for the languages you don't need and rename
    the one(s) you need appropriately. If we still consider the project
    "lube" in english, rename YOUR_PROJECT_NAME.en.tex to lube.en.tex.
    Also remove unnecessary files from the Makefile and rename the
    other(s) as you see fit. Please note that the provided file 42.png
    is only used in the templates to illustrate how to add pictures in
    your pdf. Feel free to git delete it.



III - Setup
-----------

  In order to write your subject, you need a functional LaTeX
  distribtion installed on your system. We recommand the following:

  - Linux: Texlive (via your distribution packages manager)
  - OSX: MacTex (http://tug.org/cgi-bin/mactex-download/MacTeX.pkg)

  It might be possible to work under Windows using MiKTeX, but I've
  never tested it myself and I don't know anybody who did. As a
  consequence, if you choose to work on Windows, I can't guarantee
  anything and I can't give you any support. Please, seriously
  consider switching to Linux or OSX if you experience troubles.

  For 42 students, MacTex is available for installation from the MSC
  on your session. Everything is downloaded and installed for you,
  quick and painless.

  IMPORTANT: After installation, you might need to configure your
  $PATH variable in order to allow your system to find LaTeX
  binaries. For instance, the MacTex package for OSX usually installs
  your LaTeX distribution in /usr/local/texlive/{{YEAR}}/bin/x86_64-darwin/,
  where {{YEAR}} is the latest current release.
  This folder is not part of the usual PATH, so you must add it to
  your $PATH shell variable yourself. This behaviour has also been
  witnessed under some Linux distributions and is resolved the same way.
  A reliable symptom of this problem is a 'command not found' for
  "pdflatex" when trying to build a pdf after a successful
  installation of LaTeX.

  As introduced in the previous section, the resources/ folder is a
  submodule provided by 42's Pedago team. Its content will allow you
  to create pdfs that look like genuine 42 subjects. You will NEVER
  have to change anything in those files. Never. Don't even bother
  reading them if you are not interested. The self documented templates
  for your subject provided in the subject/ folder are already
  configured to use our LaTeX resources and style classes, no
  configuration of LaTeX or additional code is expected from you,
  as long as a clean and functional LaTeX distribution is installed
  on your system.

  However, the resources/ GiT submodule must be initialized before the
  first use. If you've never used GiT submodules, please skim through
  this documentation to get a grasp of the concept:
  https://git-scm.com/book/en/v2/Git-Tools-Submodules. When you're
  done with your reading, you will probably understand that you need
  to type these two commands at the root of your repository:

    $>git submodule init
    $>git submodule update

  Also, your resources submodule might not be up to date.

    $>git submodule foreach git pull origin master

  One more step, you must install the "pygments" Python package as our
  LaTeX styles classes use this package for syntactic highlights in
  the generated pdfs. Choose your favorite Python package manager,
  like "easy_install" or "pip". For instance using "pip":

    $>sudo pip install pygments

  If you work as a user on your session and don't have admin rights,
  use the following command instead:

    $>pip install --user pygments

  You might have to add $HOME/Library/Python/2.7/bin/ to your PATH in
  order to make it work.

  Of course, installing Pygments is needed only once. If you create
  several 42Born2Peer projects, you can skip this step from the second
  time onwards.

  Last step, you must install Kwalify to use the scale validator.

    $>gem install kwalify

   If you work as a user on your session and don't have admin rights,
  use the following command instead:

    $>gem install --user kwalify

  Just like Pygments, you only have to install it once.

* **************************************************************************** *
