import { DefaultService, OpenAPI, Item, Family } from './client';
import { Viewer } from './viewer';
import { FocusSlider } from './focusslider';
import { ScaleBar } from "./scalebar";


OpenAPI.BASE = API_BASE_URL;

let viewer = null;
let currentItems: Array<Item> = null;
let families: Array<Family> = null;
//let genera: Array<Genus> = null;



/**
 * First set up the is_type button logic. If the user only wants Reference material then type filtering is not worth showing
 This function works by if is_reference button un-clicked then the is_type options disapear
 *
 */
document.addEventListener('DOMContentLoaded', () => {
  const includeNonRef = document.getElementById('includeNonReference') as HTMLInputElement;
  const disappear_is_check = document.getElementById('make_genus_and_species_IS_TYPE_buttons') as HTMLDivElement;

  function toggledisappear_is_check() {
    disappear_is_check.style.display = includeNonRef.checked ? 'block' : 'none';
  }

  toggledisappear_is_check();
  includeNonRef.addEventListener('change', toggledisappear_is_check);
});



/**
 * Populates the family select box in the dropdown menu bar.
 Defaults to 'Please select a family' so the page doesn't load with preloaded thumbnails

 ToDo: Somewhere the get_familes function is failing #Issue: 14*
 */
  export async function populateFamilySelect(): Promise<void> {
  const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
  familySelectBox.innerHTML = ''; // Clear any existing options

  // Add default "Please select" option
  const defaultOption = new Option('Please select a family', '', true, true);
  defaultOption.disabled = true;
  familySelectBox.add(defaultOption);

  const families = await DefaultService.families(CATALOG_ID);

  for (const family of families) {
    familySelectBox.add(new Option(family.name, family.id));
  }

}
/**
When family is changed the family_id is returned and used to populate genera
 */
    export function onFamilyChange() {
      const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
      if (familySelectBox.value == "")
        return;
      console.log('familychange ', JSON.stringify(familySelectBox.value));
      populateGeneraSelect(familySelectBox.value);
      showThumbnails(null, null, familySelectBox.value)
    }
 /**
Genera change works, defaults to select an option, or ALL or genera, then populates thumbnails
 */
    export function onGeneraChange() {
      const generaSelectBox = document.getElementById('genera-select') as HTMLSelectElement;
      const selectedGenus = generaSelectBox.value;

      console.log('genera change ', JSON.stringify(generaSelectBox.value));


      if (selectedGenus === '') {
        // Do nothing — waiting for a valid selection
        console.log('No genus selected yet.');
        return;
      }

      if (selectedGenus != '__ALL__') {
        populateSpeciesSelect(selectedGenus)
        showThumbnails(null, selectedGenus, null);
      }
      else {
        console.log('all genera')
        const familySelectBox = document.getElementById('family-select') as HTMLSelectElement;
        showThumbnails(null, null, familySelectBox.value);
      }
    }

//The purpose of this is to fill in the genera drop down but also if the is_genera type box not clciked we want to exclude them
    async function populateGeneraSelect(familyid: string) {
      //clear exisiting
      const generaSelectBox = document.getElementById('genera-select') as HTMLSelectElement;
      while (generaSelectBox.firstChild) {
        generaSelectBox.firstChild.remove()
      }

        // Add default "Please select a genera" option
      const defaultOption = new Option('Please select a genera', '', true, true);
      defaultOption.disabled = true;
      generaSelectBox.add(defaultOption);

      //add 'ALL' Option
      generaSelectBox.add(new Option('All', '__ALL__'));

        // Get the checkbox state for whether to include genera with is_type = True
      const generaTypeCheckbox = document.getElementById('includeGeneraType') as HTMLInputElement | null;
      const is_include_if_genus_is_type = generaTypeCheckbox ? generaTypeCheckbox.checked : true;


    // Populate genera with API call
      const genera = await DefaultService.genera(familyid, is_include_if_genus_is_type);
      for (const genus of genera) {
        generaSelectBox.add(new Option(genus.name, genus.id));
      }
      onGeneraChange();
    }

// species drop down now defaults to please select a species
// ToDo: Implement the is_type filter by species
    async function populateSpeciesSelect(generaid: string) {
        const speciesSelectBox = document.getElementById('species-select') as HTMLSelectElement;

      // Clear existing options
      while (speciesSelectBox.firstChild) {
        speciesSelectBox.firstChild.remove();
      }

      // Add default "Please select a species" option
      const defaultOption = new Option('Please select a species', '', true, true);
      defaultOption.disabled = true;
      speciesSelectBox.add(defaultOption);

      // Populate with species from the API
      if (generaid != null) {
        const speciesList = await DefaultService.species(generaid);
        for (const species of speciesList) {
          speciesSelectBox.add(new Option(species.name, species.id));
        }
      }
    }


    export function onSpeciesChange() {
      const speciesSelectBox = document.getElementById('species-select') as HTMLSelectElement;
      const selectedSpecies = speciesSelectBox.value;

      if (selectedSpecies === '') {
        console.log('No species selected yet.');
        return; // Skip if default option is still selected
      }

      showThumbnails(selectedSpecies, null, null);
    }



// Logic to  get page number display working, cant go below 0 used in get_items for pagation control
let currentPage: number = 1; // Start on page 1

document.addEventListener("DOMContentLoaded", () => {
  const nextBtn = document.getElementById("next_button") as HTMLButtonElement;
  const backBtn = document.getElementById("back_button") as HTMLButtonElement;
  const pageDisplay = document.getElementById("page-number") as HTMLSpanElement;

  const updatePageDisplay = () => {
    pageDisplay.textContent = currentPage.toString();
  };

  nextBtn.addEventListener("click", () => {
    currentPage++;
    updatePageDisplay();
  });

  backBtn.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      updatePageDisplay();
    }
  });

  // Initial display
  updatePageDisplay();
});


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





async function showThumbnails(
  species_id: string | null,
  genus_id: string | null,
  family_id: string | null) {
  if (!families) families = await DefaultService.families(CATALOG_ID);

  const gallery = document.getElementById('gallery') as HTMLDivElement;
  while (gallery.firstChild) {
    gallery.firstChild.remove();
  }

  // Ensure checkbox exists before accessing `.checked`
  const checkbox = document.getElementById('includeNonReference') as HTMLInputElement | null;
  const includeNonReference = checkbox ? checkbox.checked : true; //

  // Add const for if is_genus_check
  const generaTypeCheckbox = document.getElementById('includeGeneraType') as HTMLInputElement | null;
  const is_include_if_genus_is_type = generaTypeCheckbox ? generaTypeCheckbox.checked : true;

  // Add const for if is_species_check
  const speciesTypeCheckbox = document.getElementById('includeSpeciesType') as HTMLInputElement | null;
  const is_include_if_species_is_type = speciesTypeCheckbox ? speciesTypeCheckbox.checked : true;



  // Get type_user_max_results that is filled in from HTML. If not there default defined in main.py
  const maxResultsInput = document.getElementById('max-results-input') as HTMLInputElement | null;
  const maxResultsRaw = maxResultsInput?.value?.trim();
  const maxResults = maxResultsRaw && !isNaN(parseInt(maxResultsRaw)) ? parseInt(maxResultsRaw) : 100; // default to 100

 // Get value for page
 // const pageDisplay = document.getElementById('page-number') as HTMLSpanElement;

 try {
     let currentItems;

  if (species_id) {
    currentItems = await DefaultService.items(null, null, species_id, undefined, is_include_if_species_is_type, includeNonReference, undefined, undefined, undefined, 'abundance', maxResults, currentPage);
  } else if (genus_id) {
    currentItems = await DefaultService.items(null, genus_id, null, is_include_if_genus_is_type, undefined, includeNonReference, undefined, undefined, undefined, 'abundance', maxResults, currentPage);
  } else {
    currentItems = await DefaultService.items(family_id, null, null, undefined, undefined, includeNonReference, undefined, undefined, undefined, 'abundance', maxResults, currentPage);
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






// #TODO ======= CLEAR GALLERY AND THUMBNAILS =======
// add a box that returns the  get genera_by_letter function and place it within a box

// for alphabet fucntion to work we need to clear the Viewandinfo() first we define the fucntions and call it inside the event listner

function hideViewerAndInfo() {
  const viewer = document.getElementById('viewer-container');
  const infoPanel = document.getElementById('infopanel');
  if (viewer) viewer.style.display = 'none';
  if (infoPanel) infoPanel.style.display = 'none';
}

function showViewerAndInfo() {
  const viewer = document.getElementById('viewer-container');
  const infoPanel = document.getElementById('infopanel');
  if (viewer) viewer.style.display = 'block';
  if (infoPanel) infoPanel.style.display = 'block';
}

// What happens when you click Alphabet-filter
document.addEventListener("DOMContentLoaded", () => {
  const alphabetFilter = document.getElementById("alphabet-filter");
  const resultsContainer = document.createElement("div");
  resultsContainer.className = "results-container";

  // get result box ready that the genera will populate
  const resultsBox = document.createElement("div");
  resultsBox.id = "results-box";
  resultsBox.className = "results-box";

  resultsContainer.appendChild(resultsBox);
  document.body.appendChild(resultsContainer);

//get the letter the user wants
  if (alphabetFilter) {
    alphabetFilter.addEventListener("click", async (event: Event) => {
      const target = event.target as HTMLElement;
      if (target.tagName === "BUTTON") {
        const letter = target.getAttribute("data-letter");
        if (!letter) return;

        console.log(`Fetching genera for letter: ${letter}`);

       //clear gallery at the start of the function
        const gallery = document.getElementById('gallery') as HTMLDivElement;
        if   (gallery) {
          while (gallery.firstChild) {
            gallery.firstChild.remove();
          }
        }

        // Hide viewer + info panel to make more beautiful
        hideViewerAndInfo();

        // Get the checkbox state for whether to include genera with is_type
        const generaTypeCheckbox = document.getElementById('includeGeneraType') as HTMLInputElement | null;
        const is_include_if_genus_is_type = generaTypeCheckbox ? generaTypeCheckbox.checked : true;

        // Now we call the API using get.generaByLetter(letter)
        try {
          const genera = await DefaultService.generaByLetter(letter, is_include_if_genus_is_type);
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

// from the last step we have all the genera filled. once clicked we want to return the species.
//ToDo: filter is_type species from this species fetch #issue 16
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

    // Always add the "ALL" option, basically the same as selecting 'All' from the dropdown
    const allOption = document.createElement("div");
    allOption.className = "species-item all-option";
    allOption.innerHTML = `<strong>ALL</strong>`;
    allOption.addEventListener("click", () => {
        showViewerAndInfo();
        // Here is where the the thumbnails are fetced
      showThumbnails(null, genusId, null);
    });
    speciesContainer.appendChild(allOption);


    // If the user doesnt select all insetad they want a specific species
    if (speciesList && speciesList.length > 0) {
      speciesList.forEach((species: { id: string; name: string }) => {
        const speciesDiv = document.createElement("div");
        speciesDiv.className = "species-item";
        speciesDiv.innerHTML = `<strong>${species.name}</strong>`;

        speciesDiv.addEventListener("click", async () => {
          speciesContainer.innerHTML = ""; // Clear the species list
          // Here is where the call happens
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

