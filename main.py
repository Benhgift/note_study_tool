# This is the main file. All it does is read the the user's choice and then tell the notebook class to do whatever the user asked for. 
from lib.arg_operations import get_args, check_args, do_args

def main():
    args = get_args()
    check_args(args)
    do_args(args)

if __name__=='__main__':
    main()
