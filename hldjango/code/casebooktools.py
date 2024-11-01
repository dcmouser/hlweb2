# thin commandline wrapper for running NON-DJANGO casebook commandline utilities, etc.

# casebook tools class does all the work
from lib.casebook.cbtools import CbTools
#
from lib.jr.jrfuncs import jrprint




def main():
    # this main() is used for running commandline casebook tools
    cbtools = CbTools()
    cbtools.processCommandline()



# execute main
if __name__ == '__main__':
    main()

