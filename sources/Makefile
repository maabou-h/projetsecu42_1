NAME	=	ft_malcolm

SRCS	=	srcs/main.c		\
			srcs/packet.c	\
			srcs/addr.c		\
			srcs/ifeth.c	\
			srcs/ifsock.c

INC		=	incs/ft_malcolm.h

OBJS	=	$(SRCS:.c=.o)

LIBS	=	libft/libft.a \

CFLAGS	=	-Wall -Wextra -Werror -Iincs -Ilibft

RM		=	rm -f

all		:	$(LIBS) $(NAME)

$(NAME)	:	$(OBJS) $(INC)
	gcc $(CFLAGS) $(OBJS) $(LIBS) -o $(NAME) -Iincs

$(LIBS)	:
	$(MAKE) -C libft

clean	:
	$(RM) $(OBJS) && $(MAKE) clean -C libft

fclean	:	clean
	$(RM) $(NAME) libft/libft.a

re		:	fclean all

.PHONY : all re clean fclean
