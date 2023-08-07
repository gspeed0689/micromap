from typing import List

class MockupDataRepository:
    def get_families(self) -> List[str]:
        return ["Acanthaceae", "Achariaceae", "Achatocarpaceae", "Aextoxicaceae", "Aizoaceae",
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

    def get_genera(self, familyname: str) -> List[str]:
        if familyname == "Cannabaceae":
            return ["Aphananthe", "Cannabis", "Celtis", "Gironniera",
                    "Humulus", "Lozanella", "Pteroceltis", "Trema"]
        else:
            return []
