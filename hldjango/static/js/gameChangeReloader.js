// default monitor time
var delayShort = 1000;
var delayLong = 5000;
var delay = delayShort;
var loopCount = 0;
var loopCountThresholdSlowDown = 5
var gameMonitorList;
var gameIdListStr;
var baseSiteUrl;




//---------------------------------------------------------------------------

async function beginMonitoringForGameChanges(in_baseSiteUrl) {
    baseSiteUrl = in_baseSiteUrl;
    //console.log(`scanForGameDatesToMonitor with url = ${baseSiteUrl}.`)
    await scanForGameDatesToMonitor();
}

async function scanForGameDatesToMonitor() {
    // scall dom for all ids of form monitor_game_#
    // for each we find, keep track of this id, and periodically query the back end to get new modification dates for this game
    // if any change, reload the page.
    //console.log("scanForGameDatesToMonitor.")

    // get all elements of class "monitor_game"
    gameMonitorList = document.getElementsByClassName("monitor_game");
    // build comma separated id list of games being monitored, for making requests
    let gameIdList = []
    for (let i = 0; i < gameMonitorList.length; i++) {
        let gameMonitor = gameMonitorList[i];
        let gameId = gameMonitor.getAttribute("data-gameid")
        gameIdList.push(gameId)
    }
    gameIdListStr = gameIdList.join(",")

    // start the loop
    await checkLoop();
}




async function checkLoop() {
    if (gameMonitorList.length==0) {
        // nothing to do
        //console.log("checkLoop no games to monitor.")
        return;
    }
    setTimeout(async () => {
        // runs after delay
        //console.log(`Checking loop count # ${loopCount}.`)

        // api request, ask server for modification dates for a list of game ids
        // returns a DICTIONARY of gameid: modifiedSecs
        let modifiedGameDates = await requestModificationGameDates(gameIdListStr)

        if (typeof modifiedGameDates === 'object' && modifiedGameDates !== null) {
            // loop all 
            for (let i = 0; i < gameMonitorList.length; i++) {
                let gameMonitor = gameMonitorList[i];
                let elementId = gameMonitor.id
                let gameId = gameMonitor.getAttribute("data-gameid")
                let pageGameModificationSecs = parseInt(gameMonitor.getAttribute("data-modified"))
                //console.log(`Checking index ${i}, el ${gameId} with id ${elementId} and modSecs ${pageGameModificationSecs}.`)
                if (gameId in modifiedGameDates) {
                    // found it
                    if ("secs" in modifiedGameDates[gameId]) {
                        // found the item we expect
                        let currentGameModificationSecs = modifiedGameDates[gameId]["secs"]
                        if (currentGameModificationSecs != pageGameModificationSecs) {
                            // changed!
                            //console.log(`ELEMENT index ${i}, el ${gameId} is changed  [${currentGameModificationSecs}] vs [${pageGameModificationSecs}]!`)
                            doForceReloadPage();
                            return;
                        }
                    } else {
                        // error; for some reason not found
                        console.log(`Failed to find modified timestamps in reply for index ${i}, el ${gameId} with id ${elementId} and modSecs ${pageGameModificationSecs}.`)
                    }
                }
            }
        }

        // adjust delay
        loopCount += 1;
        if ((delay < delayLong) && (loopCount > loopCountThresholdSlowDown)) {
            delay = delayLong;
        }

        // trigger next delayed run
        await checkLoop();

    }, delay);
  };


async function requestModificationGameDates(gameIdListStrQuery) {
    let requestUrl = baseSiteUrl + gameIdListStrQuery
    let modifiedGameDates = {}

    try {
        const response = await fetch(requestUrl);
        if (!response.ok) {
          throw new Error(`Response status: ${response.status}`);
        }
    
        const json = await response.json();
        // reply is good
        modifiedGameDates = json
      } catch (error) {
        console.error(error.message);
      }

    return modifiedGameDates
}





function doForceReloadPage() {
    //console.log("Forcing page reload.")
    location.reload();
    }
//---------------------------------------------------------------------------


