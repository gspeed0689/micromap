const APIURLBase: string = "http://localhost:8000/";

function pad(num: number, size: number) {
  let numStr = num.toString();
  while (numStr.length < size) numStr = "0" + numStr;
  return numStr;
}

/**
 * Populates the family select box in the search bar.
 *
 */

function populateFamilySelect() {
  const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
  fetch(APIURLBase + "get-families/")
    .then((response) => { return response.json(); })
    .then((familyList: Families) => {
      for (const familyid in familyList) {
        const family = familyList[familyid] as Family;
        familySelectBox.add(new Option(family.name, familyid));
      }
    })
}

function onFamilyChange(selectElement: HTMLSelectElement) {
  const gallery = document.getElementById('gallery') as HTMLDivElement;
  while (gallery.firstChild) {
    gallery.firstChild.remove()
  }
  populateGeneraSelect(selectElement.value)
}

function populateGeneraSelect(familyid: string) {
  const generaSelectBox = document.getElementById('genera-select') as HTMLSelectElement;
  while (generaSelectBox.firstChild) {
    generaSelectBox.firstChild.remove()
  }

  fetch(APIURLBase + "get-genera/?familyid=" + familyid)
    .then((response) => { return response.json(); })
    .then((generaList: Genera) => {
      for (const genusid in generaList) {
        const genus = generaList[genusid] as Genus;
        generaSelectBox.add(new Option(genus.name, genusid));
      }
    })
}

function showThumbnails() {
  const gallery = document.getElementById('gallery') as HTMLDivElement;
  for (let i = 1; i < 87; i++) {
    const newDiv = document.createElement('div');

    newDiv.className = 'image-item';
    const img = document.createElement('img');
    img.src = "pollen/image" + pad(i, 3) + ".png"
    newDiv.appendChild(img);
    gallery.appendChild(newDiv);
  }
}