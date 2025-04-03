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
    showThumbnails(null, selectedGenus, null);
  }
  else {
    console.log('all genusses')
    const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
    showThumbnails(null, null, familySelectBox.value);
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
  showThumbnails(speciesSelectBox.value, null, null);
}



export async function thumbnailSelected(c: string) {
  const selectedItem = currentItems.find((element) => element.id === c);

   let infoSpan = document.getElementById('info-study-description') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.study.description;
   infoSpan = document.getElementById('info-study-location') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.study.location;
   infoSpan = document.getElementById('info-study-remarks') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.sample.study.remarks;
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
   infoSpan = document.getElementById('info-slide-remarks') as HTMLSpanElement;
   infoSpan.textContent = selectedItem.slide.remarks


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



async function showThumbnails(species_id: string | null, genus_id: string | null, family_id: string | null) {
  if (!families) families = await DefaultService.families(CATALOGID);

  const gallery = document.getElementById('gallery') as HTMLDivElement;
  while (gallery.firstChild) {
    gallery.firstChild.remove();
  }



  // Ensure checkbox exists before accessing `.checked`
  const checkbox = document.getElementById('includeNonReference') as HTMLInputElement | null;
  const includeNonReference = checkbox ? checkbox.checked : true; //

  console.log(
    `Fetching items for ${genus_id ? "genus" : "family"}: ${genus_id || family_id}, Include Non-Reference: ${includeNonReference}`
  );

 try {
  if (species_id) {
    currentItems = await DefaultService.items(null, null, species_id, includeNonReference);
  } else if (genus_id) {
    currentItems = await DefaultService.items(null, genus_id, null, includeNonReference);
  } else {
    currentItems = await DefaultService.items(family_id, null, null, includeNonReference);
  }

    if (!currentItems || currentItems.length === 0) {
      console.warn("No items found for the selected filters.");
      return;
    }

    for (const item of currentItems) {
      console.log("Rendering item:", item);

      const newDiv = document.createElement('div');
      newDiv.className = 'image-item';

      const anchor = document.createElement('a');
      anchor.href = `javascript:PollenBase.thumbnailSelected('${item.id}')`;

      const img = document.createElement('img');
      img.src = `data:image/png;base64,${item.key_image}`;
      anchor.appendChild(img);
      newDiv.appendChild(anchor);
      gallery.appendChild(newDiv);
    }
  } catch (error) {
    console.error("Error fetching thumbnails:", error);
  }
}

// add a box that returns the  get genera_by_letter function and place it within a box
document.addEventListener("DOMContentLoaded", () => {
  const alphabetFilter = document.getElementById("alphabet-filter");
  const resultsContainer = document.createElement("div");
  resultsContainer.className = "results-container";

  const resultsBox = document.createElement("div");
  resultsBox.id = "results-box";
  resultsBox.className = "results-box";

  resultsContainer.appendChild(resultsBox);
  document.body.appendChild(resultsContainer);

  if (alphabetFilter) {
    alphabetFilter.addEventListener("click", async (event: Event) => {
      const target = event.target as HTMLElement;
      if (target.tagName === "BUTTON") {
        const letter = target.getAttribute("data-letter");
        if (!letter) return;

        console.log(`Fetching genera for letter: ${letter}`);

        try {
          const genera = await DefaultService.generaByLetter(letter);
          resultsBox.innerHTML = "";

          if (!genera || genera.length === 0) {
            console.warn("No genera found.");
            resultsBox.innerHTML = "<p>No genera found.</p>";
            return;
          }

          genera.forEach((genus: { genus_id: string; genus_name: string; family_name: string }) => {
            const div = document.createElement("div");
            div.className = "result-item";
            div.dataset.genusId = genus.genus_id;
            div.innerHTML = `<strong>${genus.genus_name}</strong><br>
                             <span class="family-name">(${genus.family_name})</span>`;

            div.addEventListener("click", async () => {
              await fetchSpecies(genus.genus_id, div);
            });

            resultsBox.appendChild(div);
          });
        } catch (error) {
          console.error("Error fetching genera:", error);
        }
      }
    });
  }
}); //

//
async function fetchSpecies(genusId: string, genusElement: HTMLElement) {
  console.log(`Fetching species for genus ID: ${genusId}`);
  try {
    const speciesList = await DefaultService.species(genusId);

    let speciesContainer = genusElement.querySelector(".species-container") as HTMLElement;
    if (!speciesContainer) {
      speciesContainer = document.createElement("div");
      speciesContainer.className = "species-container";
      genusElement.appendChild(speciesContainer);
    }

    speciesContainer.innerHTML = "";

    // Always add the "ALL" option
    const allOption = document.createElement("div");
    allOption.className = "species-item all-option";
    allOption.innerHTML = `<strong>ALL</strong>`;
    allOption.addEventListener("click", () => {
      showThumbnails(null, genusId, null);
    });
    speciesContainer.appendChild(allOption);

    // If there are species, add them
    if (speciesList && speciesList.length > 0) {
      speciesList.forEach((species: { id: string; name: string }) => {
        const speciesDiv = document.createElement("div");
        speciesDiv.className = "species-item";
        speciesDiv.innerHTML = `<strong>${species.name}</strong>`;

        speciesDiv.addEventListener("click", async () => {
          speciesContainer.innerHTML = ""; // Clear the species list
          showThumbnails(species.id, null, null);
        });

        speciesContainer.appendChild(speciesDiv);
      });
    } else {
      // If there are no species, still show the ALL option
      console.warn(`No species found for genus ID: ${genusId}`);
    }
  } catch (error) {
    console.error("Error fetching species:", error);
  }
}

