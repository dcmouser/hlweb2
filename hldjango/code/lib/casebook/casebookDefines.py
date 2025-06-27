# default values that are often used in multiple places:
#  cbfuncs_core1.py (when invoking configuration functions)
#  jrastcbr.py (where data structure defaults are set)
#  cbtasks.py (where we have defaults for tasks overriding these)





# defines
DefCbVersion = "4.67"
DefCbVersionDate = "6/15/25"
DefCbVersionString = "v" + DefCbVersion + " (" + DefCbVersionDate + ")"
DefCbBuildString = "Casebook " + DefCbVersionString
DefCbAuthorString = "Jesse Reichler <jessereichler@gmail.com>"

# version changes
DefCbVersionHistory = """
# v4.67 (6/16/25)
Added new functions so that auto lead generation will be stable and consistent between runs even after changes are made.
The website now automatically saves not only source text versions every time a case source is changed, but versioned copies of all published pdfs; this will make it easier to diagnose issues.
Cover files are no longer shown in published file list (pointless)
# v4.65 (6/15/25)
Added $flatAlpha() function for images since default mac pdf reader is having a problem with alpha transparent images
# v4.64 (6/13/25)
Fixing bug with render false embed links with $inlines()
Improved comment parsing to let code better detect ane of lines for deferrred punctuation.
Fixed IRP text on some days.
Added bookmark/outline/toc with page numbers to MapInterleaved.pdf
Fixed lowercasing of "if you have circled" in a couple of places.
# v4.63 (6/12/25)
Fixing fingerprint directory toc page numbers (thx Delia)
Removed defaultTime option from configureRenderer() as its not used any more, and time set in configureSection for leads acts as default time now.
# v4.62 (6/11/25)
Added question support functions; converted Foxtrot East to use them.
# v4.61 (6/9/25)
Adding database export functions
# v4.59 (6/8/25)
Added dedicated Fingerprint Report to debug report build
Added more compact fingerprint set generation for 2-column layouts
Improved css of game list page
Improved text for links in report
# v4.58 (6/6/25)
Fixed bug error complaining about LatexFontCommant
Updated directories
Added new Campaign sort option for games
Added new filter to only show public games, for logged in users and admins
Updated sample template to compile without errors
Added link to Past is a Crooked game case as another alternate starting template
# v4.55 (6/5/25)
Removing some formats from published/draft builds to make it faster and less confusing
# v4.54 (6/3/25)
Fixed new Fingerprint directory and renamed some macro casebook files
Split Fingerprint directory into player directory and anonymous directory.
Added new 'caption' parameter to fingerprint functions so you can override caption of id
# v4.53 (6/3/25)
Updated MapAtlas.pdf (page numbers, North Harlem, more automated build)
Added a new report to debug report, an auto-walkthrough of the case
# v4.52 (6/2/25)
Updating v3 directories for PastIsACrookedGame
# v4.51 (5/31/25)
Improved debug report unused image report to not list source images that are dithered automatically.
Improved debug report yellow and person files to generate empty named files to make clear they are empty
Show campaign info for games on game details page
# v4.49 (5/29/25)
Fixed some python warnings thrown in docker.
Fixed latex error generated with columnbreaks in single column output formats
Added configureCampaign() function so you can set the base campaign name and position of the current case
Fixed bug reporting user's groups in profile
Add campaign name & position fields for games (both in casebook source and django models)
Added sorting options for game list
Added campaign name & position to game list
# v4.45 (5/27/25)
Fixed a bunch of bugs in newspaper layouts
Added flow wrapping image parameter
Added support for tag dependencies and autoHintDependency function to help hint entries not be read out of order
Added support for putting document label in footer in addition to in normal header (headingStyle="alsoFooter"); should this be the default? OR should we only have the label but no info like ("DOCUMENT 1")
# v4.43 (5/19/25)
Adding functions for reporting last questions and answers
Improved reporting of unbalanced quotes for fixing AutoQuoteStyle=true
# v4.42 (5/15/25)
Added $referDb() function to allow refering to leads by name, useful for inserting contact lists
Improve $image() so that align=left lets you put multiple images on a line (with captions) wrapping like text (see fingerprints)
# v4.41 (5/11/25)
Rewrote marker/tag letter assignment code and added new options for how marker letters are assigned
You can now set an obfuscated marker letter directly and automatic ones will avoid that letter
You can also now more easily add decoy markers using $gainDecoy() which will auto generate an obfuscated letter tag without requiring you to declare it ahead of time
# v4.40 (5/10/25)
Added reputation to the mark function for instructed players about checkboxes to tick.
Added helper function for explaining IRPs, and scheduling IRP-based events.
Added sortGroup and sortKey to optional entry parameters so that you can better fine tune sorting in unusual cases (e.g. the Hint section)
# v4.39 (5/8/25)
Wrote generic $event() function to handle scheudling of both evening events, which will be a new standard way of ending days, and more generic ones.
Improve imageBehind function to allow better padding
Improved $mark() function for demerits, reputation, etc. to make it more flexible
# v4.38 (5/7/25)
Added support for events and end-day instructions to support new system of required markers.
# v4.37 (5/4/25)
Fixed bug and improved reporting when builds failed on an older version of source and needed rebuild 
# v4.36 (5/2/25)
Updating v3 dataset to fix apartment oddities and doctor/therapist double entries
# v4.35 (4/29/25)
Adding files to support online map/play(testing) tools
Updating v3 datasets
# v4.34 (4/20/25)
Added $leave() function for boilerplate 'there is no reason for me to be here so i leave'
# v4.33 (4/18/25)
Debug version now builds a cover image so it can be used as thumbnail for internal game list.
Website now makes location data jsons available with cors support for online tools.
# v4.32 (4/17/25)
Fixed batch build errors about custom user function redefinition
Improved $blurbStop() function
Falls back to using debug cover for internal game list
Added support for $dayDate() function with "dayOfWeek" output format; support for referring to days prior to first day using negative day numbers
# v4.31 (4/13/25)
Improved labels for inline hints ("xxx contd." part)
Added ('helpful' parameters to mark $mark() function, and default inline hint text, so that it tells player to demerit only if hint was helpful. 
Made address subheading info small and italic to reduce temptation to read it.
# v4.30 (4/12/25)
Fixed but with lettrine in short newspaper articles
# v4.29 (4/9/25)
Modified newspaper headline/byline styling to take var=val| pair for more easy overriding
Moved page numbers a bit lower
# v4.27 (4/7/25)
Added database dName and address to mind map nodes for leads; added dName to table of contents lines in debug report
When you do a debug build and html version of source is created, this source can be copied and pasted to a google doc for a nicely formatted source file (headers as h1,h2, etc)
In addition, the html export now adds comments for leads that are found in the db, listing the entry name and address
Fixed github login (thanks Peter)
# v4.25 (3/26/25)
# adding get(identifier, defaultVal) and setDefault(identifier, defaultVal)
# Added variables from task configuration to environment (taskLeadSectionBreak, taskLeadSectionColumns, taskLeadBreak, taskLeadColumns); these are controlled by the prefferred or batch buiild
# You can now use these in the configuration of sections so that non-lead sections (like hints) can obey the build task settings for number of columns and lead breaks, etc.
# Prior to v4.25 only the lead section options would be changed by task options.
# In future versions, the aim will be to allow the batch task builds to be configured by author to build any number of configurations of different options, rather than preset to page formatting presets
# Added support for arbitrary font size specification in points in addition to latex preset sizes of [tiny, script, footnode, small, normal, large, Large, LARGE, Huge] by using the size string fs## or fs##.##
# Fixed issue when table of contents was not linking proplely to sections with no headiers; where label="", toc="something" where
# v4.24 (3/24/25)
# Improving admin backend model view to show user group memberships, etc.
# v4.23 (3/23/25)
# Updated home page banner image
# v4.23 (3/22/25)
# Fixed django warning in template of main menu when user is not logged in
# Again trying to fix generated files list of what version was last built
# v4.22 (3/21/25)
# Fixed oddity when reporting that last build started soon after last edit
# Separate line listed the case date separate from case system
# Replaced latex loruem ipsum with homebrew text placeholder function
# Added new lead plugin for numbered paragraphs (alphaNumeric) and leaddb variants (numbers99, numbers999, numbers9999) for unused leads
# v4.19 (3/14/25)
# Added formNumber() function for short form line/box
# Improved newspaper spacing, and spacing options; added divider and indent options
# Numbered and unnumbered lists are now formatting nicely via markdown and latex
# function $fingerprintPath() added, to be used with $image() instead of $fingerprintImage()
# v4.18 (3/13/25)
# added a function to configure the dividers used between leasds; a custom png can now bed used
# improved newspaper functions; you can now much more easily set visual features for all articles and groups in a newspaper
# you no longer have to use $newsGroup() you can just set columns in $newspaper
# you no longer have to user $newsHeadline() or $newsByline() you can now pass headling and byline as parameters in $newspaper()
# you can now set headlingStyle and bylineStyle in the $newspaper() function which will effect all articles; style string can be any pipe separated list of: bold|italic|underline|large|Large|Huge|small|fit|upper...
# v4.17 (3/12/25)
# Fixed bug in modifying global options
# Added document on upgrading case to latest version of casebook
# Added style="bordered" to images (just border no padding)
# Improved user profile; Added homepage and bggname urls, as well as a list of group memberships; links to user profile from game list page
# Fixed bug where documents were not properly referring back to the page where they were gained if they were gained in a section introduction rather than a lead
# Improved global admin settings for home and about page; added chimpmail newsletter signup to about page.
# v4.16 (3/11/25)
# Improving error messages in reporting problems parsing settings
# Improving error messages in calling function with unnknown arguments
# Fixed bug in parsing of block comments /* ... */
# v4.15 (3/5/25)
# Improved newspaper styles so you can set headline style and dropcaps options for newspaper at a whole which will filter down to articles
# Improved the look of some dropcaps effects
# Added $textup() function
# v4.13 (3/5/25)
# Fixed logging errors on production server
# v4.10 (3/4/25)
# Added reference to lead where gained for documents
# Fixing some margin layout issue on two-sided layouts when switching to footer-based titles for documents (full sized newspapers, etc.)
# Improved linespace for lead subheadings, especially for smaller page sizes
# Added version history to website about page
# v4.09
# Added code to suport language translation for casebook common text strings
# v4.07
# New marker labeling system uses A1 instead of A, and labels all markers sequentially in the order they are DEFINED; in this way you should always define prerequisite markers before those that depend on them.
# e.g. if you have a marker("cond.foundNameOfCat") and a marker ("cond.foundOutMrXHasACat") then you should define the latter before the former.
# the reason this is important is that when the casebook tells the player what tags they must find for the day, they are sorted in the order they are defined
# v4.06
# Improved form functions for questions and answers
# v4.05
# Added newspaper image dithering function (when you go to detail page of a file upload)
# v4.04
# Giving up trying to get http login to work (if we ever need to test on a new domain temporarily without https this will haunt us)
# Enforcing https redirect
# v4.03
# improved default newspaper layouts
# added options to newspaper function to control paragraph and line spacing
# v3.99
# improved logging system in django site
# added 'fit' arguement to newspaper headlines to adjust headline to fit on one line
# widths for images and format/boxes can not be specified either in % of page width, or explicitly eg "5in"
# fixed bug with draft building resulting in error on custom largefont build
# slightly improved latex error detection
# improved newspaper layout
# improved custom font underlining and strikethrough (bolder and matching color)
# v3.96 - fixed background transparency of full cover page images
# moved cover page function to latex function
# fixed bug in start and end day time to support fractional values (with minutes)
# added support for specifying day start and end as a string like "8:00 am"
# unified some image/font/finding functions
# added support for hyphenate=false in defineFont
"""



# image manager names
DefFileManagerNameImagesCase = "images_case"
DefFileManagerNameImagesShared = "images_shared"
DefFileManagerNamePdfsCase = "pdfs_case"
DefFileManagerNamePdfsShared = "pdfs_shared"
DefFileManagerNameSourceCase = "source_case"
DefFileManagerNameSourceShared = "source_shared"
DefFileManagerNameFontsShared = "fonts_shared"



# rendererData options
DefCbRenderDefault_doubleSided = True
DefCbRenderDefault_latexPaperSize = "letter"
DefCbRenderDefault_latexPaperSizesAllowed = ["letter","A4","B6","A5"]
DefCbRenderDefault_latexFontSize = 10
DefCbRenderDefault_autoStyleQuotes = False
DefCbRenderDefault_timeStyle = "box"
DefCbRenderDefault_defaultTime = -1
DefCbRenderDefault_defaultTimeStyle = "bold"
DefCbRenderDefault_zeroTimeStyle = "hide"

#
DefCbRenderDefault_latexExtraRuns = 1
DefCbRenderDefault_latexQuietMode = True
DefCbRenderDefault_latexRunViaExePath = False
#DefCbRenderDefault_latexCompiler = "pdflatex" # original
DefCbRenderDefault_latexCompiler = "xelatex" # slower but much better font support (we are moving to this as of 2/6/25)
#
DefCbRenderDefault_outputSuffix = "_test"
DefCbRenderDefault_outputSubdir = "test"
DefCbRenderDefault_renderVariant = "report"
#
DefCbRenderDefault_DropCapLineSize = 3
DefCbRenderDefault_DropCapProtectStyle = "wrap"
DefCbRenderDefault_DropCapProtectStyleNewspaper = "none"

#
DefCbTaskDefault_saveLeadJsons = True
DefCbTaskDefault_generateMindMap = True
DefCbTaskDefault_saveHtmlSource = True


# documentData options
DefCbDocumentDefault_defaultLocation = "back"
DefCbDocumentDefault_printLocation = "inline"
DefCbDocumentDefault_printStyle = "simple"


# game
DefCbGameDefault_clockMode = True


# tag options
DefCbRenderSettingDefault_Tag_alwaysNumber = True
DefCbRenderSettingDefault_Tag_consistentNumber = True
DefCbRenderSettingDefault_Tag_mode = "sequential" # ["sequential", "random", "firstLetter"]
DefCbRenderSettingDefault_Tag_sortRequire = True

# locale
DefCbLocaleDefault_language = "en"


# fixed values
# not used currently but available for testing
# we do NOT let the user change this because doing so would be a security risk
#DefCbDefine_latexExeFullPath = "C:/Users/jesse/AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe"

DefCbDefine_TopLevelDividers = True
DefCbDefine_ParseDayConfigureDate = "%m/%d/%Y"


# for new game creations
DefCbDefine_NewGameStartingSourceTemlateUrl = "https://docs.google.com/document/d/1am1HNjGZhSgjJKIvRkTmadlxXIiuXZxycIfxuhEV-lo/edit?usp=sharing"
DefCbDefine_NewGameSimpleSourceTemlateUrl = "https://docs.google.com/document/d/1Cpb-VsxSrc0XeI6vAnIhbDHyrD9iSJ6untZPYTlcjH0/edit?usp=sharing"

# defines
DefLatexVouchedPrefix = "LATEX:"
DefLatexVouchedEmbeddablePrefix = "LATEXEMBED:"
DefContdStr = "contd."
DefInlineLeadPlaceHolder = "(see other lead)"
DefInlineLeadLabelStart = "inline - "


# result notes
DefCbResultNoteTypePreArticleBodyEnd = "newspaperPreArticleBodyEnd"