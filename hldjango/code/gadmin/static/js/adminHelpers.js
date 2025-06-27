function loadUrlDisplayInElement(url, elementId, flagAddRefresh) {
    const element = document.getElementById(elementId);
    // Set the "Loading..." message
    element.style.display = "block";
    element.innerHTML = "Loading...";

    fetch(url)
        .then(response => response.text())
        .then(data => {
            if (flagAddRefresh) {
                refreshHtml = "[<a href=\"javascript:void(0);\" onclick=\"loadUrlDisplayInElement('" + url + "', 'logContents', true)\">refresh</a>] "
                data = refreshHtml + data
            }
            element.innerHTML = data;
        })
        .catch(error => console.error('Error loading the URL:', error));
}
