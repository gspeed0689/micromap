import { DefaultService, OpenAPI } from './client';

OpenAPI.BASE = "http://localhost:8000";

function pad(num: number, size: number) {
  let numStr = num.toString();
  while (numStr.length < size) numStr = "0" + numStr;
  return numStr;
}

/**
 * Populates the family select box in the search bar.
 *
 */
export async function populateFamilySelect(): Promise<void> {
  const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
  let selectedid = null;

  const families = await DefaultService.families();

  for (const family of families) {
    if (selectedid == null)
      selectedid = family.id;
    familySelectBox.add(new Option(family.name, family.id));
  }
  if (selectedid) {
    familySelectBox.value = selectedid;
    onFamilyChange();
  }
 }

export function onFamilyChange() {
  const gallery = document.getElementById('gallery') as HTMLDivElement;
  while (gallery.firstChild) {
    gallery.firstChild.remove()
  }
  const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
  populateGeneraSelect(familySelectBox.value);
}

export function onGeneraChange() {
  const generaSelectBox = document.getElementById('genera-select') as HTMLSelectElement;
  populateSpeciesSelect(generaSelectBox.value)
}

async function populateGeneraSelect(familyid: string) {
  const generaSelectBox = document.getElementById('genera-select') as HTMLSelectElement;
  while (generaSelectBox.firstChild) {
    generaSelectBox.firstChild.remove()
  }

  const genera = await DefaultService.genera(familyid);
  for (const genus of genera) {
    generaSelectBox.add(new Option(genus.name, genus.id));
  }
}

async function populateSpeciesSelect(generaid: string) {
  const speciesSelectBox = document.getElementById('species-select') as HTMLSelectElement;
  while (speciesSelectBox.firstChild) {
    speciesSelectBox.firstChild.remove()
  }

  const speciesList = await DefaultService.species(generaid);
  for (const species of speciesList) {
    speciesSelectBox.add(new Option(species.name, species.id));
  }
}

export function onSpeciesChange() {
  const speciesSelectBox = document.getElementById('species-select') as HTMLSelectElement;
  showThumbnails(speciesSelectBox.value);
}

function showThumbnails(id: string) {
  if (id != '9cd23abd-2c09-435b-86e9-93f2827fb721')
    return;

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

