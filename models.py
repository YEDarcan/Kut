from dataclasses import dataclass, field, asdict
from typing import List, Optional

@dataclass
class MapPin:
    id: str
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    color: str = "#ef4444"
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            color=data.get("color", "#ef4444"),
            description=data.get("description", "")
        )

    def to_dict(self):
        return asdict(self)

@dataclass
class Character:
    code: str
    name: str
    title: str = ""
    gender: str = "Bilinmiyor"
    nation: str = "Bilinmiyor"
    country: str = "Bilinmiyor"
    has_magic: bool = False
    magic_type: str = ""
    description: str = ""
    image_base64: str = ""

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            code=data.get("Karakter Kodu", ""),
            name=data.get("Ad", ""),
            title=data.get("Ünvan", ""),
            gender=data.get("Cinsiyet", "Bilinmiyor"),
            nation=data.get("Millet", "Bilinmiyor"),
            country=data.get("Ülke", "Bilinmiyor"),
            has_magic=data.get("Büyü Gücü Var", False),
            magic_type=data.get("Büyü Tipi", ""),
            description=data.get("Açıklama", ""),
            image_base64=data.get("Görsel", "")
        )

    def to_dict(self):
        return {
            "Karakter Kodu": self.code,
            "Ad": self.name,
            "Ünvan": self.title,
            "Cinsiyet": self.gender,
            "Millet": self.nation,
            "Ülke": self.country,
            "Büyü Gücü Var": self.has_magic,
            "Büyü Tipi": self.magic_type,
            "Açıklama": self.description,
            "Görsel": self.image_base64
        }

@dataclass
class Chapter:
    id: str
    title: str
    content: str = ""

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            content=data.get("content", "")
        )

    def to_dict(self):
        return asdict(self)

@dataclass
class GovUnit:
    name: str
    details: str = ""
    sub_units: List['GovUnit'] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("birim", ""),
            details=data.get("detay", ""),
            sub_units=[cls.from_dict(sub) for sub in data.get("alt_birimler", [])]
        )

    def to_dict(self):
        return {
            "birim": self.name,
            "detay": self.details,
            "alt_birimler": [unit.to_dict() for unit in self.sub_units]
        }

@dataclass
class Country:
    id: str
    name: str
    government_details: List[GovUnit] = field(default_factory=list)
    geography_details: str = ""
    story: str = ""
    flag_normal: str = ""
    flag_war: str = ""
    flag_aid: str = ""

    @classmethod
    def from_dict(cls, data: dict):
        gov_details = data.get("government_details", [])
        if isinstance(gov_details, str): # Handle legacy string format
            gov_details = [{"birim": "Eski Detay", "detay": gov_details, "alt_birimler": []}]
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            government_details=[GovUnit.from_dict(unit) for unit in gov_details],
            geography_details=data.get("geography_details", ""),
            story=data.get("story", ""),
            flag_normal=data.get("flag_normal", ""),
            flag_war=data.get("flag_war", ""),
            flag_aid=data.get("flag_aid", "")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "government_details": [unit.to_dict() for unit in self.government_details],
            "geography_details": self.geography_details,
            "story": self.story,
            "flag_normal": self.flag_normal,
            "flag_war": self.flag_war,
            "flag_aid": self.flag_aid
        }
