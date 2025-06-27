# helper for creating pdf files from latex

# my libs
from . import jrfuncs
from .jrfuncs import jrprint, jrlog

# python
import os
import subprocess
from subprocess import PIPE
import shutil
import time
import tempfile
import uuid



# ---------------------------------------------------------------------------
MODE_BATCH = 0
MODE_NON_STOP = 1
MODE_SCROLL = 2
MODE_ERROR_STOP = 3
INTERACTION_MODES = ['batchmode', 'nonstopmode', 'scrollmode', 'errorstopmode']
# ---------------------------------------------------------------------------

































# ---------------------------------------------------------------------------
# this class is invoked by our main jrpdf functions in certain modes

class JrPDFLaTeX:
    def __init__(self, latex_src, job_name: str):
        self.latex = latex_src
        self.job_name = job_name
        self.interaction_mode = INTERACTION_MODES[MODE_BATCH]
        self.dir = None
        self.pdf_filename = None
        self.params = dict()
        self.pdf = None
        self.log = None
        self.rememberedOutputDirectory = None
        self.setJobFName("file_" + job_name)
        self.setCompiler("pdflatex")


    def setCompiler(self, val):
        if (val in ["pdflatex", "xelatex"]):
            self.setLatexExeBaseName(val)
        else:
            raise Exception("Unknown latex compiler '{}'.".format(val))

    def setJobFName(self, val):
        self.jobName = val
    def getJobFName(self):
        return self.jobName
    def getJobFNameWithExt(self, ext):
        return self.jobName + ext



    def getLatexExeBaseName(self):
        return self.latexExeBaseName
    def setLatexExeBaseName(self, val):
        self.latexExeBaseName = val

    @classmethod
    def from_texfile(cls, filename):
        prefix = os.path.basename(filename)
        prefix = os.path.splitext(prefix)[0]
        with open(filename, 'rb') as f:
            fileContents = cls.from_binarystring(f.read(), prefix)
            return fileContents

    @classmethod
    def from_binarystring(cls, binstr: str, jobname: str):
        return cls(binstr, jobname)

    @classmethod
    def from_jinja_template(cls, jinja2_template, jobname: str = None, **render_kwargs):
        tex_src = jinja2_template.render(**render_kwargs)
        fn = jinja2_template.filename
        
        if fn is None:
            fn = jobname
            if not fn:
                raise ValueError("PDFLaTeX: if jinja template does not have attribute 'filename' set, "
                                 "'jobname' must be provided")
        return cls(tex_src, fn)

    def create_pdf(self, keep_pdf_file: bool = False, keep_log_file: bool = False, env: dict = None, optionTimeout=None):
        if self.interaction_mode is not None:
            self.add_args({'-interaction-mode': self.interaction_mode})
        self.add_args({'-halt-on-error':None})
        #self.add_args({'-interaction': 'nonstopmode', '-halt-on-error':None})
        #self.add_args({'-interaction': 'nonstopmode'})
        
        dir = self.params.get('-output-directory')
        filename = self.params.get('-jobname')
        
        if filename is None:
            filename = self.job_name
        if dir is None:
            dir = ""
        
        with tempfile.TemporaryDirectory() as tdTemp:
            # EVIL
            if (self.rememberedOutputDirectory is None):
                td = tdTemp
                self.set_output_directory(td)
            else:
                td = self.rememberedOutputDirectory
            
            self.set_pdf_jobname(self.getJobFName())

            # test it doesnt like blank lines - this messes things up
            oldLen = len(self.latex)
            #self.latex = self.latex.replace(b'\n\n',b'\n')
            #self.latex = self.latex.replace(b'\r\n',b'\n')
            newLen = len(self.latex)
    
            args = self.get_run_args()
            fp = subprocess.run(args, input=self.latex, env=env, timeout=optionTimeout, stdout=PIPE, stderr=PIPE)
            fileFullPath = os.path.join(td, self.getJobFNameWithExt('.pdf'))
            logFullPath = os.path.join(td, self.getJobFNameWithExt('.log'))
            #
            if (os.path.exists(logFullPath)):
                with open(logFullPath, 'rb') as f:
                    self.log = f.read()
                if keep_log_file:
                    shutil.move(os.path.join(td, self.getJobFNameWithExt('.log')), os.path.join(dir, filename + '.log'))
            else:
                self.log = "ERROR: Log file not generated: {}".format(logFullPath)
            #
            if (os.path.exists(fileFullPath)):
                with open(fileFullPath, 'rb') as f:
                    self.pdf = f.read()
                if keep_pdf_file:
                    shutil.move(os.path.join(td, self.getJobFNameWithExt('.pdf')), os.path.join(dir, filename + '.pdf'))
            else:
                self.pdf = None
                if (type(self.log) is not str):
                    # evil
                    self.log = self.log.decode('latin-1')
                self.log += "\nERROR: Pdf file not generated: {}.".format(fileFullPath)
        
        return self.pdf, self.log, fp, logFullPath, fileFullPath

    def get_run_args(self):
        a = [k+('='+v if v is not None else '') for k, v in self.params.items()]
        latexExeBaseName = self.getLatexExeBaseName()
        a.insert(0, latexExeBaseName)
        return a
    
    def add_args(self, params: dict):
        for k in params:
            self.params[k] = params[k]
    
    def del_args(self, params):
        if isinstance(params, str):
            params = [params]

        if isinstance(params, dict) or isinstance(params, list):
            for k in params:
                if k in self.params.keys():
                    del self.params[k]
        else:
            raise ValueError('PDFLaTeX: del_cmd_params: parameter must be str, dict or list.')
    
    def set_output_directory(self, dir: str = None):
        self.rememberedOutputDirectory = dir
        self.generic_param_set('-output-directory', dir)

    def set_output_format(self, fmt: str = None):
        if fmt and fmt not in ['pdf', 'dvi']:
            raise ValueError("PDFLaTeX: Format must be either 'pdf' or 'dvi'.")
        self.generic_param_set('-output-format', dir)
    
    def generic_param_set(self, param_name, value):
        if value is None:
            if param_name in self.params.keys():
                del self.params[param_name]
        else:
            self.params[param_name] = value

    def set_pdf_jobname(self, jobname: str = None):
        self.generic_param_set('-jobname', jobname)
    
    def set_pdf_filename(self, pdf_filename: str = None):
        self.set_jobname(pdf_filename)
    
    def set_batchmode(self, on: bool = True):
        self.interaction_mode = INTERACTION_MODES[MODE_BATCH] if on else None

    def set_nonstopmode(self, on: bool =True):
        self.interaction_mode = INTERACTION_MODES[MODE_NON_STOP] if on else None

    def set_scrollmode(self, on: bool = True):
        self.interaction_mode = INTERACTION_MODES[MODE_SCROLL] if on else None

    def set_errorstopmode(self, on: bool = True):
        self.interaction_mode = INTERACTION_MODES[MODE_ERROR_STOP] if on else None

    def set_interaction_mode(self, mode: int = None):
        if mode is None:
            self.interaction_mode = None
        elif 0 <= mode <= 3:
            self.interaction_mode = INTERACTION_MODES[mode]
        else:
            raise ValueError('PDFLaTeX: Invalid interaction mode!')

# ---------------------------------------------------------------------------

































# ---------------------------------------------------------------------------

# outer functions

class JrPdf():
    def __init__(self):
        self.clearBuildLog()
        self.setJobFName("fileTmp_"+str(uuid.uuid4()))

    def setJobFName(self, val):
        self.jobFName = val
    def getJobFName(self):
        return self.jobFName

    def setRenderOptions(self, renderOptions):
        self.renderOptions = renderOptions


    def generatePdflatex(self, filepath, flagDebug, flagCleanExtras):
        maxRuns = 7
        #
        filePathAbs = os.path.abspath(filepath)
        outputDirName = os.path.dirname(filePathAbs)
        baseFileName = os.path.basename(filepath)
        baseFileNameNoExt = os.path.splitext(baseFileName)[0]
        currentWorkingDir = os.getcwd()
        os.chdir(outputDirName)
        # evil
        #decodeCharSet = 'ascii'
        decodeCharSet = 'latin-1'
        #
        flagSwitchToNonQuietOnError = False
        # timeout after 10 minutes running latex
        optionTimeout = 60 * 10
        #
        latexQuietMode = jrfuncs.getDictValue(self.renderOptions, 'latexQuietMode')
        #
        errored = False
        pdfl = None
        #
        optionLatexCompiler = jrfuncs.getDictValue(self.renderOptions, 'latexCompiler')

        extraTimesToRun = jrfuncs.getDictValue(self.renderOptions, 'latexExtraRuns')

        # how to run latex compile
        optionLatexRunViaExePath = jrfuncs.getDictValue(self.renderOptions,"latexRunViaExePath")
        if (optionLatexRunViaExePath):
            # pdf latex executable manually specified
            latexFullPath = jrfuncs.getDictValue(self.renderOptions, 'latexExeFullPath')
            # try this
        else:
            # use pdflatex to invoke
            # nothing to do up here
            pass

        logFilePath = None
        pdfFilePath = None

        # ATTN: new try deleting temp files first
        try:
            jrfuncs.deleteExtensionFilesIfExists(outputDirName, baseFileNameNoExt, ['aux','out','toc','log','pdf'])
            # not temp files but real files
            jrfuncs.deleteExtensionFilesIfExists(outputDirName, baseFileNameNoExt, ['log','pdf'])
            #
            jrfuncs.deleteExtensionFilesIfExists(outputDirName, self.getJobFName(), ['aux','out','toc','pdf','log'])
        except Exception as e:
            # if there is an error deleting, note that error and return
            msg = jrfuncs.exceptionPlusSimpleTraceback(e, "deleting temp files for latex compilation")
            jrlog(msg)
            return False


        wantBreak = 0
        for i in range(0,maxRuns):
            runCount = i

            if (optionLatexRunViaExePath):
                jrprint('{}. Launching pdflatex ({}) on "{}".'.format(i+1, latexFullPath, filePathAbs))
                proc=subprocess.Popen([latexFullPath, filePathAbs], stdin=PIPE, stdout=PIPE)
                [stdout_data, stderr_data] = proc.communicate()
                if (stdout_data is not None):
                    stdOutText = jrfuncs.jrSafeDecodeCharSet(stdout_data, decodeCharSet)
                else:
                    stdOutText = ''
                #
                if (stderr_data is not None):
                    stdErrText = jrfuncs.jrSafeDecodeCharSet(stderr_data, decodeCharSet)
                else:
                    stdErrText = ''
            else:
                # use pdflatex to invoke
                # see https://pypi.org/project/pdflatex/
                # works BUT seems to fail on re-running because it uses different temp file each time? FUCKED
                try:
                    if (pdfl is None):
                        pdfl = JrPDFLaTeX.from_texfile(filePathAbs)
                        pdfl.setCompiler(optionLatexCompiler)
                        pdfl.setJobFName(self.getJobFName())
                        # see https://stackoverflow.com/questions/71991645/python-3-7-pdflatex-filenotfounderror
                        pdfl.set_interaction_mode()  # setting interaction mode to None.
                        #pdfl.set_interaction_mode(3)  # setting interaction mode (INTERACTION_MODES = ['batchmode', 'nonstopmode', 'scrollmode', 'errorstopmode'])
                    else:
                        # multiple runs
                        pass
                    #pdflArgs = {"-output-directory": outputDirName}
                    #pdfl.add_args(pdflArgs)
                    pdfl.set_output_directory(outputDirName)
                    pdf, log, completed_process, logFilePath, pdfFilePath = pdfl.create_pdf(keep_pdf_file=False, keep_log_file=False, optionTimeout=optionTimeout)
                    stdout_data = log
                    stdOutText = jrfuncs.jrSafeDecodeCharSet(log, decodeCharSet)
                    #stdErrText = jrfuncs.jrSafeDecodeCharSet(completed_process.stderr, decodeCharSet) + "\n" + jrfuncs.jrSafeDecodeCharSet(completed_process.stdout,decodeCharSet)
                    stdErrText = jrfuncs.jrSafeDecodeCharSet(completed_process.stderr, decodeCharSet)
                    if (stdErrText is not None) and (len(stdErrText)>2):
                        stderr_data = stdErrText.encode(decodeCharSet)
                    else:
                        stderr_data = None
                except Exception as e:
                    try:
                        # terrible pdflatex error
                        msg = jrfuncs.exceptionPlusSimpleTraceback(e,"INITIAL pdflatex exception on '{}'; trying without keeping files...".format(filePathAbs))
                        jrprint(msg)
                        pdf, log, completed_process, logFilePath, pdfFilePath = pdfl.create_pdf(keep_pdf_file=False, keep_log_file=False, optionTimeout=optionTimeout)
                        stdout_data = log
                        stdOutText = jrfuncs.jrSafeDecodeCharSet(log, decodeCharSet)
                        stdErrText = completed_process.stderr + "\n" + completed_process.stdout
                        stderr_data = stdErrText.encode(decodeCharSet)
                    except Exception as e:
                        msg = jrfuncs.exceptionPlusSimpleTraceback(e,"Initial exception (error occurred) running pdflatex on '{}'".format(filePathAbs))
                        jrprint(msg)
                        stdOutText = ''
                        stdErrText = msg
                        stdout_data = stdOutText.encode(decodeCharSet)
                        stderr_data = stdErrText.encode(decodeCharSet)
                        if (stderr_data is None):
                            stdErrText = "Exception during initial pdflatex run (error occurred)"
                            stderr_data = stdErrText.encode(decodeCharSet)

            # check for error
            if (type(stdout_data) is str):
                stdout_data = stdout_data.encode(decodeCharSet)
            #errorStrings = [b'error occurred', b'error occurred', 'LATEX ERROR:', 'Emergency stop', '! Undefined control sequence']
            # THIS IS ABSOLUTELTY #%&**#%&#* INFURIATING
            # PDF ERRORS
            errorStrings = ['error occurred', 'LATEX ERROR:', 'Emergency stop', 'Undefined control sequence', 'Error: Undefined', 'doesn\'t match its definition', '! Package pgfkeys Error', '! File ended while scanning', '! Illegal unit', '! Too many }', '! Too many {', '! LaTeX Error', '! Missing number', '! Missing', '! Package calc Error:', '! You can', '! Paragraph ended', '! Text line contains', '! Package', '! Improper ']
            if (self.outputContainsAnyError(errorStrings, [stdout_data, stderr_data, stdOutText])):
                jrprint('\nERROR RUNNING PDF LATEX on {}!\n\n'.format(filepath))
                msg = 'Error encountered running latex.\n'
                if (stdErrText != ''):
                    stdErrText += '. '
                stdErrText += msg
                if (flagSwitchToNonQuietOnError):
                    latexQuietMode = False
                errored = True
                wantBreak = 9999
                self.addBuildLog(stdErrText, True)

            # pdflatex may require multiple runs
            if (b'Rerun to' not in stdout_data):
                wantBreak += 1
            # kludge to run multiple times
            if (wantBreak > extraTimesToRun):
                break


        if (runCount>=maxRuns-1):
            jrprint('WARNING: MAX RUNS ENCOUNTERED ({}) -- PROBABLY AN ERROR RUNNING PDFLATEX.'.format(runCount))

        # moving files if we use pdflatex
        # ATTN: changing these to copies, and doing delete later; as we had an exception on no permission to delete file
        if (logFilePath is not None):
            if (os.path.exists(logFilePath)):
                #shutil.move(logFilePath, os.path.join(outputDirName, baseFileNameNoExt + '.log'))
                shutil.copy(logFilePath, os.path.join(outputDirName, baseFileNameNoExt + '.log'))
            else:
                jrprint("ERROR: expected to find log file at {} but it's not there.".format(logFilePath))
                errored = True

        if (pdfFilePath is not None):
            if (os.path.exists(pdfFilePath)):
                #shutil.move(pdfFilePath, os.path.join(outputDirName, baseFileNameNoExt + '.pdf'))
                shutil.copy(pdfFilePath, os.path.join(outputDirName, baseFileNameNoExt + '.pdf'))
            else:
                jrprint("ERROR: expected to find pdf file at {} but it's not there.".format(pdfFilePath))
                errored = True

        # delete temporary files (this seems to fail sometimes -- still in use? docker issue only?)
        if (not errored):
            maxDeleteRetries = 5
            deleteTries = 0
            while (True):
                try:
                    jrfuncs.deleteExtensionFilesIfExists(outputDirName, baseFileNameNoExt, ['aux','out','toc'])
                    jrfuncs.deleteExtensionFilesIfExists(outputDirName, self.getJobFName(), ['aux','out','toc', 'pdf', 'log'])
                    break
                except Exception as e:
                    deleteTries += 1
                    if (deleteTries>=maxDeleteRetries):
                            exceptionMsg = jrfuncs.exceptionPlusSimpleTraceback(e, 'trying to clean delete temporary latex producted files')
                            jrprint('Failed to delete temporary latex produced files {} times; aborting: {}'.format(deleteTries, exceptionMsg))
                            break
                    # sleep and try again
                    jrprint('Failed to delete temporary latex produced files; retrying delete #{}..'.format(deleteTries))
                    time.sleep(1)
            if (deleteTries>0):
                if (deleteTries<maxDeleteRetries):
                    jrprint('Succeeded deleteing temporary files after {} retries.'.format(deleteTries))

        # change working directory back? is this still neeeded?
        os.chdir(currentWorkingDir)

        if (not latexQuietMode):
            jrprint('PDFLATEX OUTPUT:')
            jrprint(stdOutText)

        # to log regardless
        jrlog('PDFLATEX OUTPUT:')
        jrlog(stdOutText)
        

        baseFileName = os.path.basename(filepath)
        if (stderr_data is not None):
            jrprint('PDFLATEX ERR processing "{}": {}'.format(baseFileName, stdErrText))
        if (not errored):
            self.addBuildLog('Pdf generation of "{}" from Latex completed successfully ({} runs).'.format(baseFileName, runCount), False)
            jrfuncs.deleteExtensionFilesIfExists(outputDirName, self.getJobFName(), ['aux','out','toc', 'pdf', 'log'])
        else:
            self.addBuildLog('\n\n----------\nError generating "{}".\nFULL LATEX OUTPUT: {}\n{}\n'.format(baseFileName, stdOutText, stdErrText), True)

        if (flagCleanExtras):
            if (not errored):
                # delete .latex and .log files, and any other temp files that survived somehow
                try:
                    jrfuncs.deleteExtensionFilesIfExists(outputDirName, baseFileNameNoExt, ['log','latex'])
                    # others should already be gone?
                    if (True):
                        jrfuncs.deleteExtensionFilesIfExists(outputDirName, baseFileNameNoExt, ['aux','out','toc'])
                        #jrfuncs.deleteExtensionFilesIfExists(outputDirName, self.getJobFName(), ['aux','out','toc', 'pdf', 'log'])
                except Exception as e:
                    # error deleting don't worry about it
                    pass
        
        return (not errored)


# ---------------------------------------------------------------------------
    def outputContainsAnyError(self, errorStrings, errorSources):
        for errorString in errorStrings:
            errrorStringAsBytes = str.encode(errorString)
            for errorSource in errorSources:
                if (errorSource is None):
                    continue
                if (type(errorSource) is bytes):
                    if (errrorStringAsBytes in errorSource):
                        return True
                elif (errorString in errorSource):
                    return True
        return False
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
    def clearBuildLog(self):
        self.buildLog = ''
        self.buildErrorStatus = False
        self.buildErrorCount = 0

    def getBuildLog(self):
        return self.buildLog

    def getBuildErrorStatus(self):
        return self.buildErrorStatus
    def getBuildErrorCount(self):
        return self.buildErrorCount

    def addBuildErrorStatus(self):
        self.buildErrorStatus = True
        self.buildErrorCount += 1


    def addBuildLog(self, msg, isError):
        if (isError):
            self.addBuildErrorStatus()
        if (self.buildLog != ''):
            self.buildLog += '\n-----\n'
        self.buildLog += msg
# ---------------------------------------------------------------------------





