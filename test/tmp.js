document.addEventListener('DOMContentLoaded', function() {
    // Adds an event listener to form submission (to do the DOM manipulation for the demo page)
    let formElement = document.querySelector('#search-form');
    formElement.addEventListener('submit', submitForm);

    // LogUI control code
    startLogUIClient();
});

/*
    Handle a fake form submission.
    This simply does some DOM manipulation by creating new elements.
*/
function submitForm(e) {
    e.preventDefault();

    document.querySelector('#submit-button').disabled = true;

    setTimeout(() => {
        let queryString = document.querySelector('#input-box').value;

        if (queryString.length == 0) {
            alert("Please don't submit a blank query!");
            return;
        }

        let queryTextElement = document.querySelector('#query-text');
        queryTextElement.innerHTML = queryString;

        document.querySelector('#left-rail-results').innerHTML = '';
        document.querySelector('#entity-card').style.display = 'block';

        addFakeResults();
        document.querySelector('#submit-button').disabled = false;

        document.querySelector('#landing-instructions').style.display = 'none';
        document.querySelector('.results-stats').style.display = 'block';
    },
    350);
}

/*
    Adds five fake results to the DOM.
*/
function addFakeResults() {
    let fakeResults = [
        `<li data-rank="1">
            <span class="title"><a href="https://www.tudelft.nl" target="_blank">Delft University of Technology</a></span>
            <span class="url">https://www.tudelft.nl</span>
            <span class="snippet">Delft University of Technology also known as TU Delft, is the oldest and largest Dutch public technological university. </span>
        </li>`,
        `<li data-rank="2">
            <span class="title"><a href="https://en.wikipedia.org/wiki/Delft" target="_blank">Delft - Wikipedia</a></span>
            <span class="url">http://en.wikipedia.org/wiki/Delft</span>
            <span class="snippet">Delft is a popular tourist destination in the Netherlands, famous for its historical connections with the reigning House of Orange-Nassau, for its blue pottery, for...</span>
        </li>`,
        `<li data-rank="3">
            <span class="title"><a href="https://en.wikipedia.org/wiki/Delftware" target="_blank">Delftware - Wikipedia</a></span>
            <span class="url">http://en.wikipedia.org/wiki/Delftware</span>
            <span class="snippet">Delftware or Delft pottery, also known as Delft Blue (Dutch: Delfts blauw), is a general term now used for Dutch tin-glazed earthenware, a form of faience.</span>
        </li>`,
        `<li data-rank="4">
            <span class="title"><a href="https://www.holland.com/global/tourism/destinations/more-destinations/delft.htm" target="_blank">Visit Delft - These are the best things to do - Holland.com</a></span>
            <span class="url">https://www.holland.com/</span>
            <span class="snippet">Delft is famous for its ceramic Delft Blue pottery. It is known as the birth place of the famous painter Johannes Vermeer, known from "the girl with the Pearl". And it is known as a charming canal-ringed town with historical monuments and medieval architecture.</span>
        </li>`,
        `<li data-rank="5">
            <span class="title"><a href="https://www.delft.nl" target="_blank">Homepage | Gemeente Delft</a></span>
            <span class="url">http://www.delft.nl</span>
            <span class="snippet">Municipality Delft · Municipal services. Moving from abroad · Reporting a change of address · Official matters. Immigration procedure · Housing. Housing in the ...</span>
        </li>`,
    ];

    for (let result of fakeResults) {
        appendFakeResult(result);
    }

}

function appendFakeResult(markupString) {
    let resultsContainer = document.querySelector('#left-rail-results');

    let tempContainer = document.createElement('div');
    tempContainer.innerHTML = markupString.trim();

    resultsContainer.appendChild(tempContainer.firstChild);
}

/*
    A sample function that shows you how to control the LogUI library -- specifically, starting it.
*/
async function startLogUIClient() {
    if (window.LogUI) {
        // let json_init = {
        //     method: 'GET',
        //     headers: {
        //         'Content-Type': 'application/json'
        //     },
        //     mode:'cors',
        //     credentials: 'omit',
        //     referrerPolicy: 'unsafe-url',
        //     cache:'default'
        // }

        // let json_req = new Request("file:///home/rkochar/Projects/Python/Selenium/logui-example-apps/sample-search/static/js", json_init)
        // const json_object = fetch(json_req)
        // .then(response => response.json())
        // .catch(console.log)

        // ./settings.json?v=${randomVersion}
        // let config = {}
        // let response = await fetch(`file:///home/rkochar/Projects/Python/Selenium/logui-example-apps/sample-search/static/js`);
        // let obj = await response.json();
        //
        // for (var prop in obj) config[prop] = obj[prop];

        // LogUI.init(config)
        // return;
        // fetch('./../../../../test/config_object.json').then(config_data =>

        let configurationObject = {
            logUIConfiguration: {
                endpoint: 'ws://linuxvm:8000/ws/endpoint/',
                authenticationToken: 'eyJ0eXBlIjoibG9nVUktYXV0aGVudGljYXRpb24tb2JqZWN0IiwiYXBwbGljYXRpb25JRCI6IjJhZGZkOGEyLWRlOWUtNDRiNS05ZTg2LTAzNTI4OGY2ZTcxZiIsImZsaWdodElEIjoiZWZmMWQwNDEtNmUzZS00NmFmLTk1MTAtOWRlNWUwNTc4MGExIn0:1lPXp2:v9gt6oZNSUtEr9UkXsm406FTyrl65DcDrPJrTQZ24MQ',
                verbose: true,
                browserEvents: {
                    blockEventBubbling: true,
                    eventsWhileScrolling: true,
                    URLChanges: true,
                    contextMenu: true,
                    pageFocus: true,
                    trackCursor: true,
                    cursorUpdateFrequency: 4000,
                    cursorLeavingPage: true,
                },
            },
            applicationSpecificData: {
                userID: 'test_rahul1',
            },
            trackingConfiguration: {
                'querybox-focus': {
                    selector: '#input-box',
                    event: 'focus',
                    name: 'QUERYBOX_FOCUS'
                },
                'querybox-losefocus': {
                    selector: '#input-box',
                    event: 'blur',
                    name: 'QUERYBOX_BLUR'
                },
                'querybox-change': {
                    selector: '#input-box',
                    event: 'keyup',
                    name: 'QUERYBOX_CHANGE',
                    metadata: [
                        {
                            nameForLog: 'value',
                            sourcer: 'elementProperty',
                            lookFor: 'value',
                        }
                    ]
                },
                'query-submission': {
                    selector: '#search-form',
                    event: 'formSubmission',
                    name: 'QUERY_SUBMITTED',
                    properties: {
                        includeValues: [
                            {
                                nameForLog: 'completeQuery',
                                sourcer: 'elementProperty',
                                selector: '#input-box',
                                lookFor: 'value',
                            }
                        ]
                    }
                },
                'left-rail-item-mousemovements': {
                    selector: '#left-rail-results li',
                    event: 'mouseHover',
                    properties: {
                        mouseenter: {
                            name: 'LEFT_RAIL_RESULT_HOVER_IN',
                        },
                        mouseleave: {
                            name: 'LEFT_RAIL_RESULT_HOVER_OUT',
                        }
                    },
                    metadata: [
                        {
                            nameForLog: 'resultRank',
                            sourcer: 'elementAttribute',
                            lookFor: 'data-rank',
                        }
                    ]
                },
                'left-rail-item-mouseclick': {
                    selector: '#left-rail-results li span.title a',
                    event: 'contextmenu',
                },
                'entity-mousemovements': {
                    selector: '#entity-card',
                    event: 'mouseHover',
                    properties: {
                        mouseenter: {
                            name: 'ENTITY_CARD_HOVER_IN',
                        },
                        mouseleave: {
                            name: 'ENTITY_CARD_HOVER_OUT',
                        }
                    },
                }
            },
        };

        LogUI.init(configurationObject);
        return;
    }

    throw Error("We can't find the LogUI client library. Did you include the logui.bundle.js file in the static directory?");
}