from typing import List, Dict
import uuid
import random

from .models import Family, Genus

class MockupDataRepository:
    def __init__(self):
        self.rd = random.Random()
        self.rd.seed(88)

        self.families = ["Acanthaceae", "Achariaceae", "Achatocarpaceae", "Aextoxicaceae", "Aizoaceae",
            "Akaniaceae", "Alismataceae", "Allisoniaceae", "Alseuosmiaceae", "Alstroemeriaceae",
            "Altingiaceae", "Alzateaceae", "Amaranthaceae", "Annonaceae", "Antheliaceae",
            "Anthocerotaceae", "Aphanopetalaceae", "Aphloiaceae", "Apiaceae", "Apocynaceae",
            "Apodanthaceae", "Aponogetonaceae", "Aspleniaceae", "Asteliaceae", "Asteropeiaceae",
            "Atherospermataceae", "Aulacomniaceae", "Austrobaileyaceae", "Aytoniaceae",
            "Balanopaceae", "Balanophoraceae", "Balantiopsaceae", "Betulaceae", "Biebersteiniaceae",
            "Bignoniaceae", "Bixaceae", "Blandfordiaceae", "Blechnaceae", "Bonnetiaceae", "Boraginaceae",
            "Boryaceae", "Boweniaceae", "Brachytheciaceae", "Buxbaumiaceae", "Byblidaceae",
            "Calophyllaceae", "Calycanthaceae", "Calyceraceae", "Calymperaceae", "Calypogeiaceae",
            "Campanulaceae", "Campyneumataceae", "Canellaceae", "Cannabaceae", "Cannaceae",
            "Capparaceae", "Caprifoliaceae", "Cardiopteridaceae", "Caricaceae", "Carlemanniaceae",
            "Caryocaraceae", "Caryophyllaceae", "Casuarinaceae", "Catagoniaceae", "Catoscopiaceae",
            "Celastraceae", "Centrolepidaceae", "Centroplacaceae", "Cephalotaceae", "Cephalotaxaceae",
            "Cephaloziaceae", "Cephaloziellaceae", "Ceratophyllaceae", "Cercidiphyllaceae",
            "Chaetophyllopsaceae", "Chloranthaceae", "Chonecoleaceae", "Chrysobalanaceae",
            "Cinclidotaceae", "Circaeasteraceae", "Cistaceae", "Cleomaceae", "Clethraceae", "Cleveaceae"]
        self.family_keys = [str(uuid.UUID(int=self.rd.getrandbits(128))) for _ in range(len(self.families))]


    def get_families(self) -> Dict[str, Family]:
        result = {}
        for i, familyname in enumerate(self.families):
            result[self.family_keys[i]] = Family(familyname)
        return result


    def get_genera(self, familyid: str) -> Dict[str, Genus]:
        if familyid == "be5f3713-8771-bc64-79a8-fb302e64ec56": # Cannabaceae
            self.rd.seed(89)
            genera = ["Aphananthe", "Cannabis", "Celtis", "Gironniera",
                    "Humulus", "Lozanella", "Pteroceltis", "Trema"]
            keys = [str(uuid.UUID(int=self.rd.getrandbits(128))) for _ in range(len(genera))]
            result = {}
            for i, genus_name in enumerate(genera):
                result[keys[i]] = Genus(genus_name)
            return result
        elif familyid == "9a09a699-23ff-579d-b035-28e91f539270": # Akaniaceae
            self.rd.seed(90)
            genera = ["Akania", "Bretschneidera"]
            keys = [str(uuid.UUID(int=self.rd.getrandbits(128))) for _ in range(len(genera))]
            result = {}
            for i, genus_name in enumerate(genera):
                result[keys[i]] = Genus(genus_name)
            return result
        else:
            return {}

