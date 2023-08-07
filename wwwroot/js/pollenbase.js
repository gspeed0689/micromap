function populateFamilySelect()
{
    var familySelectBox = document.getElementById('family-select');
    fetch("http://localhost:8000/get-families/").then((response) => {return response.json();}).then((familyList) => {
        for(var familyName of familyList)
            familySelectBox.add(new Option(familyName, familyName));
    })
}

function populateGeneraSelect(familyName)
{
    var generaSelectBox = document.getElementById('genera-select');
    while (generaSelectBox.firstChild) {
        generaSelectBox.firstChild.remove()
    }

    fetch("http://localhost:8000/get-genera/?familyname=" + familyName).then((response) => {return response.json();}).then((generaList) => {
        for(var generaName of generaList)
        generaSelectBox.add(new Option(generaName, generaName));
    })
}

function onFamilyChange(selectElement) {
    var gallery = document.getElementById('gallery');
    while (gallery.firstChild) {
        gallery.firstChild.remove()
    }
    populateGeneraSelect(selectElement.value)
}

function pad(num, size) {
    num = num.toString();
    while (num.length < size) num = "0" + num;
    return num;
}

function showThumbnails() {
    var gallery = document.getElementById('gallery')
    for (var i = 1; i < 87; i++) {
        var newDiv = document.createElement('div');

        newDiv.className = 'image-item';
        var img = document.createElement('img');
        img.src = "pollen/image" + pad(i, 3) + ".png"
        newDiv.appendChild(img);
        gallery.appendChild(newDiv);
    }
}