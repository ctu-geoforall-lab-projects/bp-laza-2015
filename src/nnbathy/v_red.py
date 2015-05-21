#!/usr/bin/env python
####################################################################
# MODULE:     v.surf.nnbathy.py
#
# AUTHOR(S):  Adam Laza (mentor: Martin Landa)
#             (based on v.surf.nnbathy from GRASS 6)
####################################################################
from nnbathy import Nnbathy_vector, Nnbathy_file

def main():
    # initial controls
    if (options['input'] and options['file']):
        grass.fatal("Please specify either the 'input' \
                    or 'file' option, not both.")

    if not(options['input'] or options['file']):
        grass.message("Please specify either the 'input' or 'file' option.")

    if (options['file'] and os.path.isfile(options['file'])):
        grass.message("File "+options['file']+" does not exist.")

    # vector or file input?
    if (options['input']):
        obj = Nnbathy_vector(options)
    else:
        obj = Nnbathy_file(options)

    obj.compute()
    obj.create_output()

if __name__ == "__main__":
    options, flags = parser()
    main()
