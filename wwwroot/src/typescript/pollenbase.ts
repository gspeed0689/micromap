import { DefaultService, OpenAPI } from './client';

OpenAPI.BASE = "http://localhost:8000";

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

  const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
  populateGeneraSelect(familySelectBox.value);
}

export function onGeneraChange() {
  const generaSelectBox = document.getElementById('genera-select') as HTMLSelectElement;
  populateSpeciesSelect(generaSelectBox.value)
  showThumbnails(generaSelectBox.value);
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

export function showcomment(c: string)
{
  const comment_div = document.getElementById('info-container') as HTMLDivElement;
  comment_div.innerHTML = c;
}

async function showThumbnails(id: string) {
  const gallery = document.getElementById('gallery') as HTMLDivElement;
  while (gallery.firstChild) {
    gallery.firstChild.remove()
  }

  const items = await DefaultService.items(null, id);

  for (const item of items) {
    const newDiv = document.createElement('div');
    newDiv.className = 'image-item';
    const anchor = document.createElement('a');
    const link = "javascript:PollenBase.showcomment('" + (item.comment !== null ? item.comment as string : "") + "')";
    console.log(link);
    anchor.href= link;
    //anchor.onclick = () => showcomment(;

    const img = document.createElement('img');
    img.src = "data:image/png;base64," + item.key_image;
    anchor.appendChild(img);
    newDiv.appendChild(anchor);
    gallery.appendChild(newDiv);
  }
}

