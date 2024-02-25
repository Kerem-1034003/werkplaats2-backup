let activeFilters = []
var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {return new bootstrap.Popover(popoverTriggerEl)})

function setSearchValue(){
    document.getElementById('searchLink').setAttribute('href', '/vraag/' + searchInput.value)
}


function fixMarkeer(element) {
    markeerLabel = document.getElementById("markeerLabel")
    if (element.checked) {
        markeerLabel.innerText = ''
        newI = document.createElement('i')
        newI.setAttribute('class', 'bi bi-bookmark-fill')
        markeerText = document.createTextNode(" Gemarkeerd")
        markeerLabel.appendChild(newI)
        markeerLabel.appendChild(markeerText)
        document.getElementById('markeerValue').value = 1
    }
    else {
        markeerLabel.innerText = ''
        newI = document.createElement('i')
        newI.setAttribute('class', 'bi bi-bookmark')
        markeerText = document.createTextNode(" Markeer")
        markeerLabel.appendChild(newI)
        markeerLabel.appendChild(markeerText)
        document.getElementById('markeerValue').value = 0
    }
}

function cleanUpSelect(element){
    datatype_group = document.getElementById("datatype-group")

    if (element.value == "VARCHAR"){
        newInput = document.createElement("input");
        newInput.setAttribute("id", "amount-of-varchar")
        newInput.setAttribute("name", "datatype-amount-of-varchar")
        newInput.setAttribute("class", "form-control")
        newInput.setAttribute("type", "number")
        newInput.setAttribute("aria-describedby", "amountGroupAddon")
        datatype_group.appendChild(newInput)
    }
    else {
        if(document.getElementById("amount-of-varchar")){
            document.getElementById("amount-of-varchar").remove()
        }
    }
}

function copyId(element) {
  navigator.clipboard.writeText(element.innerText);
}

function toggleFilter(element) {

    const filterElm = document.getElementById(element.value)

    if (filterElm == null) {
        const filterButtonsContainer = document.getElementById("filterButtonsContainer");
        const newButton = document.createElement("button");
        const buttonText = document.createTextNode(element.value + " ")
        newButton.setAttribute("class", "btn btn-secondary tc-button");
        newButton.setAttribute("id", element.value);
        newButton.appendChild(buttonText)
        filterButtonsContainer.appendChild(newButton)

        activeFilters.push(element.value)
    }
    else {
        activeFilters = activeFilters.filter(function(e) { return e !== element.value })
        filterElm.remove()
    }
    console.log(activeFilters)
}

function processFilters(tableBody) {
    tableBody.innerHTML = ''
    data.forEach(vraag => processTags(vraag, tableBody));
}

function processTags(vraag, tableBody){
    if (vraag.tags.some(r=> activeFilters.includes(r))) {
        const newTr = document.createElement("tr");
            const newTdId = document.createElement("td");
                const idText = document.createTextNode(vraag.id)
                newTdId.appendChild(idText)
            const newTdVraag = document.createElement("td");
                const vraagText = document.createTextNode(vraag.vraag)
                newTdVraag.appendChild(vraagText)
            const newTdLeerdoel = document.createElement("td");
                const leerdoelText = document.createTextNode(vraag.leerdoel)
                newTdLeerdoel.appendChild(leerdoelText)
            const newTdAuteur = document.createElement("td");
                const auteurText = document.createTextNode(vraag.auteur)
                newTdAuteur.appendChild(auteurText)
            const newTdTags = document.createElement("td");
                vraag.tags.forEach(tag => createTag(tag, newTdTags))
            const newTdEditButton = document.createElement("td");
                const newA = document.createElement("a");
                newA.setAttribute("href", "/vraag/" + vraag.id);
                newA.setAttribute("class", "btn btn-success");
                    const newI = document.createElement("i");
                    newI.setAttribute("class", "bi bi-pencil");
                newA.appendChild(newI)
            newTdEditButton.appendChild(newA)

        newTr.appendChild(newTdId)
        newTr.appendChild(newTdVraag)
        newTr.appendChild(newTdLeerdoel)
        newTr.appendChild(newTdAuteur)
        newTr.appendChild(newTdTags)
        newTr.appendChild(newTdEditButton)

        tableBody.appendChild(newTr)
    }

}

function createTag(tag, newTdTags){
    const tagText = document.createTextNode(tag)
    const newSpan = document.createElement("span");
    newSpan.setAttribute("class", "badge rounded-pill bg-secondary");
    newSpan.appendChild(tagText)
    newTdTags.appendChild(newSpan)
}

function giveCheckValue(element){
    if (element.checked) {
        element.value = 1
    }
    else{
        element.value = 0
    }
}

function removeOptions(selectElement) {
   var i, L = selectElement.options.length - 1;
   for(i = L; i >= 0; i--) {
      selectElement.remove(i);
   }
}

function generateOption(){

}

function generateColumnSelect(element) {
    columnSelect = document.getElementById('columnSelect')
    removeOptions(columnSelect);
    selectedOption = element.options[element.selectedIndex].value

    if (selectedOption == "Kies een tabel..."){
        columnSelect.setAttribute('disabled', 'true')
        newOption = document.createElement('option')
        newOption.innerText = "Kies tabel eerst!"
        columnSelect.appendChild(newOption)
    }
    else{
        columnSelect.removeAttribute('disabled')
        newOption = document.createElement('option')
        newOption.innerText = "Kies een kolom..."
        columnSelect.appendChild(newOption)
    }

    for (var i = 0; i < table_info.length; i++) {
        if(selectedOption == table_info[i].tabel) {
            for (const column of table_info[i].columns){
                newOption = document.createElement('option')
                newOption.innerText = column
                columnSelect.appendChild(newOption)
            }
        }
    }

}

function tableToCSV() {

    // Variable to store the final csv data
    var csv_data = [];

    // Get each row data
    var rows = document.getElementsByTagName('tr');
    for (var i = 0; i < rows.length; i++) {

        // Get each column data
        var cols = rows[i].querySelectorAll('td,th');

        // Stores each csv row data
        var csvrow = [];
        for (var j = 0; j < cols.length; j++) {

            // Get the text data of each cell
            // of a row and push it to csvrow
            csvrow.push(cols[j].innerHTML);
        }

        // Combine each column value with comma
        csv_data.push(csvrow.join(","));
    }

    // Combine each row data with new line character
    csv_data = csv_data.join('\n');

    // Call this function to download csv file
    downloadCSVFile(csv_data);

}

function downloadCSVFile(csv_data) {

    // Create CSV file object and feed
    // our csv_data into it
    CSVFile = new Blob([csv_data], {
        type: "text/csv"
    });

    // Create to temporary link to initiate
    // download process
    var temp_link = document.createElement('a');

    // Download csv file
    temp_link.download = "Test-correct-tussenwaardes.csv";
    var url = window.URL.createObjectURL(CSVFile);
    temp_link.href = url;

    // This link should not be displayed
    temp_link.style.display = "none";
    document.body.appendChild(temp_link);

    // Automatically click the link to
    // trigger download
    temp_link.click();
    document.body.removeChild(temp_link);
}