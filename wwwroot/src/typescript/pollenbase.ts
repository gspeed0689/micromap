import { DefaultService, OpenAPI, Item, Family } from './client';
import { Viewer } from './viewer';
import { FocusSlider } from './focusslider';
import { ScaleBar } from "./scalebar";

OpenAPI.BASE = 'http://localhost:8000';
const CATALOGID = 'b788163e-cc97-4333-85f0-f7de210fe416';
let viewer = null;
let currentItems: Array<Item> = null;
let families: Array<Family> = null;
//let genera: Array<Genus> = null;

/**
 * Populates the family select box in the search bar.
 *
 */
export async function populateFamilySelect(): Promise<void> {
  const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
  let selectedid = null;

  const families = await DefaultService.families(CATALOGID);

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
  if (familySelectBox.value == "")
    return;
  console.log('familychange ', JSON.stringify(familySelectBox.value));
  populateGeneraSelect(familySelectBox.value);
}

export function onGeneraChange() {
  const generaSelectBox = document.getElementById('genera-select') as HTMLSelectElement;
  console.log('genera change ', JSON.stringify(generaSelectBox.value));
  const selectedGenus = generaSelectBox.value;
  if (selectedGenus != '__ALL__') {
    populateSpeciesSelect(selectedGenus)
    showThumbnails(selectedGenus, null);
  }
  else {
    console.log('all genusses')
    const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
    showThumbnails(null, familySelectBox.value);
  }
}

async function populateGeneraSelect(familyid: string) {
  const generaSelectBox = document.getElementById('genera-select') as HTMLSelectElement;
  while (generaSelectBox.firstChild) {
    generaSelectBox.firstChild.remove()
  }

  generaSelectBox.add(new Option('All', '__ALL__'));

  const genera = await DefaultService.genera(familyid);
  for (const genus of genera) {
    generaSelectBox.add(new Option(genus.name, genus.id));
  }
  onGeneraChange();
}

async function populateSpeciesSelect(generaid: string) {
  return;
  if (generaid == null)
    return;

  const speciesSelectBox = document.getElementById('species-select') as HTMLSelectElement;
  while (speciesSelectBox.firstChild) {
    speciesSelectBox.firstChild.remove()
  }

  if (generaid != null) {
    const speciesList = await DefaultService.species(generaid);
    for (const species of speciesList) {
      speciesSelectBox.add(new Option(species.name, species.id));
    }
  }
}

export function onSpeciesChange() {
  const speciesSelectBox = document.getElementById('species-select') as HTMLSelectElement;
  showThumbnails(speciesSelectBox.value, null);
}

export async function thumbnailSelected(c: string) {
  const selectedItem = currentItems.find((element) => element.id === c);

   let infoSpan = document.getElementById('info-study-description') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.study.description;
   infoSpan = document.getElementById('info-study-location') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.study.location;
   infoSpan = document.getElementById('info-study-remarks') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.study.remarks;

   infoSpan = document.getElementById('info-sample-description') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.description
   infoSpan = document.getElementById('info-sample-location') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.location
   infoSpan = document.getElementById('info-sample-age') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.age
   infoSpan = document.getElementById('info-sample-remarks') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.remarks

   infoSpan = document.getElementById('info-slide-description') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.description
   infoSpan = document.getElementById('info-slide-location') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.location;


  const f: string[] = ['prepared/o_' + c + '/' + c + '_1.png',
  'prepared/o_' + c + '/' + c + '_2.png',
  'prepared/o_' + c + '/' + c + '_3.png',
  'prepared/o_' + c + '/' + c + '_4.png',
  'prepared/o_' + c + '/' + c + '_5.png'
  ];

  viewer = new Viewer('#viewer-container', 'viewer', 400, 400, f, null);
  const slider = new FocusSlider(viewer, "#viewer-focus-slider");
  const scaleBar = new ScaleBar(viewer, "#viewer-scalebar", selectedItem.voxel_width);
}

async function showThumbnails(genus_id: string, family_id: string) {
  if (families == null)
    families = await DefaultService.families(CATALOGID);

  const gallery = document.getElementById('gallery') as HTMLDivElement;
  while (gallery.firstChild) {
    gallery.firstChild.remove()
  }

  if (genus_id != null) {
    currentItems = await DefaultService.items(null, genus_id);
  }
  else {
    console.log('genus = all')
    currentItems = await DefaultService.items(family_id, null);
  }

  for (const item of currentItems) {
    console.log(item);
    const newDiv = document.createElement('div');
    newDiv.className = 'image-item';
    //const family = families.find((family) => family.id === item.family_id);
    //newDiv.title = family.name;
    const anchor = document.createElement('a');
    const link = "javascript:PollenBase.thumbnailSelected('" + item.id + "')";
    anchor.href = link;

    const img = document.createElement('img');
    img.src = "data:image/png;base64," + item.key_image;
    anchor.appendChild(img);
    newDiv.appendChild(anchor);
    gallery.appendChild(newDiv);
  }
}
