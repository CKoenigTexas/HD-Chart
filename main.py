from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import swisseph as swe
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz


app = FastAPI(title="ROI of Peace — Human Design API")

# Allow requests from any frontend (Netlify, Wix, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Swiss Ephemeris setup ──────────────────────────────────────────────────
swe.set_ephe_path("/app/ephe")  # Railway ephemeris files location

# ── Planet constants ───────────────────────────────────────────────────────
PLANETS = {
    "sun":        swe.SUN,
    "earth":      None,          # Earth = Sun + 180°
    "north_node": swe.TRUE_NODE,
    "south_node": None,          # South Node = North Node + 180°
    "moon":       swe.MOON,
    "mercury":    swe.MERCURY,
    "venus":      swe.VENUS,
    "mars":       swe.MARS,
    "jupiter":    swe.JUPITER,
    "saturn":     swe.SATURN,
    "uranus":     swe.URANUS,
    "neptune":    swe.NEPTUNE,
    "pluto":      swe.PLUTO,
}

# ── HD gate sequence (64 hexagrams mapped to ecliptic, starting from Aries) ──
# Each gate spans 5.625° (360 / 64). Sequence starts at HD offset from 0° Aries.
HD_OFFSET_DEGREES = 302.0  # Gate 41 starts at 2° Aquarius = 302° absolute

GATE_SEQUENCE = [
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
    27, 24,  2, 23,  8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
    31, 33,  7,  4, 29, 59, 40, 64, 47,  6, 46, 18, 48, 57, 32, 50,
    28, 44,  1, 43, 14, 34,  9,  5, 26, 11, 10, 58, 38, 54, 61, 60
]

GATE_NAMES = {
    1:"Self-Expression", 2:"Receptivity", 3:"Ordering", 4:"Formulization",
    5:"Fixed Rhythms", 6:"Friction", 7:"The Role of the Self", 8:"Contribution",
    9:"Focus", 10:"Behavior of the Self", 11:"Ideas", 12:"Caution",
    13:"The Listener", 14:"Power Skills", 15:"Modesty", 16:"Skills",
    17:"Following", 18:"Correction", 19:"Wanting", 20:"The Now",
    21:"Biting Through", 22:"Openness", 23:"Assimilation", 24:"Rationalization",
    25:"Innocence", 26:"The Trickster", 27:"Caring", 28:"The Game Player",
    29:"Perseverance", 30:"Recognition of Feelings", 31:"Leading", 32:"Continuity",
    33:"Privacy", 34:"Power", 35:"Change", 36:"Crisis", 37:"Friendship",
    38:"Opposition", 39:"Provocation", 40:"Aloneness", 41:"Contraction",
    42:"Growth", 43:"Insight", 44:"Coming to Meet", 45:"Gathering Together",
    46:"Pushing Upward", 47:"Realization", 48:"The Well", 49:"Revolution",
    50:"Values", 51:"The Arousing", 52:"Stillness", 53:"Beginnings",
    54:"Ambition", 55:"Abundance", 56:"Stimulation", 57:"The Gentle",
    58:"Vitality", 59:"Sexuality", 60:"Acceptance", 61:"Mystery",
    62:"Preponderance of the Small", 63:"Doubt", 64:"Confusion"
}

# ── Center gate assignments ────────────────────────────────────────────────
CENTER_GATES = {
    "HEAD":   [64, 61, 63],
    "AJNA":   [47, 24, 4, 17, 43, 11],
    "THROAT": [62, 23, 56, 35, 12, 45, 33, 8, 31, 20, 16],
    "G":      [7, 1, 13, 10, 25, 15, 46, 2],
    "SACRAL": [5, 14, 29, 59, 9, 3, 42, 27, 34],
    "EGO":    [21, 40, 26, 51],
    "SPLEEN": [48, 57, 44, 50, 32, 28, 18],
    "SOLAR":  [30, 55, 49, 37, 22, 36, 6],
    "ROOT":   [60, 52, 19, 39, 53, 54, 58, 38, 41]
}

# ── Channel pairs ──────────────────────────────────────────────────────────
CHANNELS = [
    (1,8),(2,14),(3,60),(4,63),(5,15),(6,59),(7,31),(9,52),(10,20),(11,56),
    (12,22),(13,33),(16,48),(17,62),(18,58),(19,49),(20,34),(20,57),(21,45),
    (23,43),(24,61),(25,51),(26,44),(27,50),(28,38),(29,46),(30,41),(32,54),
    (33,13),(34,57),(35,36),(37,40),(39,55),(42,53),(43,23),(44,26),(45,21),
    (46,29),(47,64),(48,16),(49,19),(50,27),(51,25),(52,9),(53,42),(54,32),
    (55,39),(56,11),(57,20),(58,18),(59,6),(60,3),(61,24),(62,17),(63,4),(64,47)
]

# ── Helpers ────────────────────────────────────────────────────────────────
def longitude_to_gate_line(lon: float) -> dict:
    """Convert ecliptic longitude (0–360) to HD gate and line."""
    gate_span = 360.0 / 64.0          # 5.625° per gate
    line_span  = gate_span / 6.0      # 0.9375° per line

    adjusted   = (lon - HD_OFFSET_DEGREES) % 360
    gate_index = int(adjusted / gate_span) % 64
    line       = int((adjusted % gate_span) / line_span) + 1
    line       = min(line, 6)         # clamp safety

    gate = GATE_SEQUENCE[gate_index]
    return {"gate": gate, "line": line, "name": GATE_NAMES.get(gate, "")}


def get_planet_longitude(jd: float, planet_key: str) -> float:
    """Return ecliptic longitude for a planet at a given Julian Day."""
    # Use high-precision flag for all calculations
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    if planet_key == "earth":
        sun_lon = swe.calc_ut(jd, swe.SUN, flags)[0][0]
        return (sun_lon + 180.0) % 360.0

    if planet_key == "south_node":
        nn_lon = swe.calc_ut(jd, swe.TRUE_NODE, flags)[0][0]
        return (nn_lon + 180.0) % 360.0

    planet_id = PLANETS[planet_key]
    result = swe.calc_ut(jd, planet_id, flags)
    return result[0][0]


def get_center_for_gate(gate: int) -> str | None:
    for center, gates in CENTER_GATES.items():
        if gate in gates:
            return center
    return None


def determine_type_strategy_authority(defined_centers: set, defined_channels: list) -> dict:
    has_sacral  = "SACRAL"  in defined_centers
    has_throat  = "THROAT"  in defined_centers
    has_solar   = "SOLAR"   in defined_centers
    has_spleen  = "SPLEEN"  in defined_centers
    has_ego     = "EGO"     in defined_centers
    has_g       = "G"       in defined_centers

    # Motor-to-throat connection check
    motor_centers = {"SACRAL", "ROOT", "SOLAR", "EGO"}
    motor_to_throat = False
    for (a, b) in defined_channels:
        ca = get_center_for_gate(a)
        cb = get_center_for_gate(b)
        if (ca in motor_centers and cb == "THROAT") or \
           (cb in motor_centers and ca == "THROAT"):
            motor_to_throat = True
            break

    # Type
    if has_sacral and not motor_to_throat:
        hd_type   = "Generator"
        strategy  = "Respond to what lights you up. Let your gut guide your yes and no."
        not_self  = "Frustration"
        signature = "Satisfaction"
    elif has_sacral and motor_to_throat:
        hd_type   = "Manifesting Generator"
        strategy  = "Respond first, then inform before you act. It's okay to skip steps."
        not_self  = "Frustration & Anger"
        signature = "Satisfaction & Peace"
    elif not has_sacral and motor_to_throat:
        hd_type   = "Manifestor"
        strategy  = "Inform those who will be affected before you act."
        not_self  = "Anger"
        signature = "Peace"
    elif not has_sacral and not has_throat and len(defined_centers) == 0:
        hd_type   = "Reflector"
        strategy  = "Wait a full lunar cycle (28 days) before making major decisions."
        not_self  = "Disappointment"
        signature = "Surprise"
    else:
        hd_type   = "Projector"
        strategy  = "Wait for the invitation in work, relationships, and major decisions."
        not_self  = "Bitterness"
        signature = "Success"

    # Authority
    if has_solar:
        authority = "Emotional"
        auth_desc = "Sleep on decisions. Clarity comes in waves, not all at once."
    elif has_sacral:
        authority = "Sacral"
        auth_desc = "Trust your gut response — the immediate yes or no in your body."
    elif has_spleen:
        authority = "Splenic"
        auth_desc = "Trust the quiet, in-the-moment instinct. It speaks once and softly."
    elif has_ego:
        authority = "Will"
        auth_desc = "Make decisions based on what you truly want and are willing to commit to."
    elif has_g:
        authority = "Self-Projected"
        auth_desc = "Talk it out with people you trust. Hearing your own voice brings clarity."
    elif "HEAD" in defined_centers or "AJNA" in defined_centers:
        authority = "Mental"
        auth_desc = "Talk through decisions with different trusted people and notice what resonates."
    else:
        authority = "Timing"
        auth_desc = "Track how you feel across a full lunar cycle before committing."

    return {
        "type": hd_type,
        "strategy": strategy,
        "not_self": not_self,
        "signature": signature,
        "authority": authority,
        "authority_desc": auth_desc,
    }


def get_profile_name(line1: int, line2: int) -> str:
    names = {
        (1,4): "The Investigator / Opportunist",
        (2,5): "The Hermit / Heretic",
        (3,6): "The Martyr / Role Model",
        (4,1): "The Opportunist / Investigator",
        (5,2): "The Heretic / Hermit",
        (6,3): "The Role Model / Martyr",
        (1,3): "The Investigator / Martyr",
        (2,4): "The Hermit / Opportunist",
        (3,5): "The Martyr / Heretic",
        (4,6): "The Opportunist / Role Model",
        (5,1): "The Heretic / Investigator",
        (6,2): "The Role Model / Hermit",
    }
    return names.get((line1, line2), f"{line1}/{line2}")


# ── Request / Response models ──────────────────────────────────────────────
class ChartRequest(BaseModel):
    name: str = ""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str          # "Lansing, Michigan, United States"


# ── Main endpoint ──────────────────────────────────────────────────────────
@app.post("/chart")
def calculate_chart(req: ChartRequest):
    try:
        # 1. Geocode birth city → lat/lng
        geolocator = Nominatim(user_agent="roi-of-peace-hd")
        location   = geolocator.geocode(req.city, timeout=10)
        if not location:
            raise HTTPException(status_code=400, detail=f"Could not find city: {req.city}")

        lat, lng = location.latitude, location.longitude

        # 2. Get timezone for that lat/lng
        tf       = TimezoneFinder()
        tz_name  = tf.timezone_at(lat=lat, lng=lng)
        if not tz_name:
            raise HTTPException(status_code=400, detail="Could not determine timezone for that location.")

        tz       = pytz.timezone(tz_name)
        local_dt = datetime(req.year, req.month, req.day, req.hour, req.minute)
        local_aware = tz.localize(local_dt, is_dst=None)
        utc_dt   = local_aware.astimezone(pytz.utc)

        # 3. Julian Day (UT) — use Swiss Ephemeris utc_to_jd for maximum precision
        # Returns (jd_et, jd_ut) tuple
        jd_result = swe.utc_to_jd(
            utc_dt.year, utc_dt.month, utc_dt.day,
            utc_dt.hour, utc_dt.minute, float(utc_dt.second),
            swe.GREG_CAL
        )
        birth_jd = jd_result[1]  # jd_ut — Universal Time Julian Day
        # Design date: exactly 88 degrees of solar arc before birth
        # Newton-Raphson method using Sun's actual speed for fast convergence
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        birth_sun_data = swe.calc_ut(birth_jd, swe.SUN, flags)[0]
        birth_sun_lon = birth_sun_data[0]
        target_lon = (birth_sun_lon - 88.0) % 360.0
        design_jd = birth_jd - 90.0  # Good starting estimate (~88 days)
        for _ in range(20):
            sun_data = swe.calc_ut(design_jd, swe.SUN, flags)[0]
            current_lon = sun_data[0]
            sun_speed = sun_data[3]  # degrees/day (actual speed from Swiss Ephemeris)
            diff = (target_lon - current_lon + 180) % 360 - 180
            if abs(diff) < 0.0000001:  # ~0.00036 arcseconds — extremely precise
                break
            design_jd += diff / sun_speed  # Newton-Raphson step

        # 4. Calculate planet positions for both dates
        planet_keys = list(PLANETS.keys())

        personality = {}
        design      = {}

        for key in planet_keys:
            p_lon = get_planet_longitude(birth_jd,  key)
            d_lon = get_planet_longitude(design_jd, key)
            personality[key] = longitude_to_gate_line(p_lon)
            design[key]      = longitude_to_gate_line(d_lon)

        # 5. Collect activated gates
        personality_gates = set(v["gate"] for v in personality.values())
        design_gates      = set(v["gate"] for v in design.values())
        all_gates         = personality_gates | design_gates

        # 6. Find defined channels
        defined_channels = [
            (a, b) for (a, b) in CHANNELS
            if a in all_gates and b in all_gates
        ]

        # 7. Find defined centers
        defined_centers = set()
        for (a, b) in defined_channels:
            for gate in (a, b):
                c = get_center_for_gate(gate)
                if c:
                    defined_centers.add(c)

        # 8. Type / Strategy / Authority
        core = determine_type_strategy_authority(defined_centers, defined_channels)

        # 9. Profile
        # Line 1 = Personality Sun line (conscious)
        # Line 2 = Design Earth line (unconscious)
        sun_line   = personality["sun"]["line"]
        earth_line = design["earth"]["line"]
        profile_name = get_profile_name(sun_line, earth_line)
        profile = f"{sun_line}/{earth_line} — {profile_name}"

        # 10. Build response
        return {
            "name": req.name,
            "birth": {
                "local": f"{req.year}-{req.month:02d}-{req.day:02d} {req.hour:02d}:{req.minute:02d}",
                "city": req.city,
                "timezone": tz_name,
                "utc": utc_dt.strftime("%Y-%m-%d %H:%M UTC"),
            },
            "type":           core["type"],
            "strategy":       core["strategy"],
            "not_self":       core["not_self"],
            "signature":      core["signature"],
            "authority":      core["authority"],
            "authority_desc": core["authority_desc"],
            "profile":        profile,
            "profile_lines":  [sun_line, earth_line],
            "personality":    personality,
            "design":         design,
            "personality_gates": sorted(list(personality_gates)),
            "design_gates":      sorted(list(design_gates)),
            "all_gates":         sorted(list(all_gates)),
            "defined_channels":  defined_channels,
            "defined_centers":   sorted(list(defined_centers)),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ── PDF Generation via ReportLab (Styled) ─────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus.flowables import RoundedRect
import io

class PDFChartRequest(BaseModel):
    name: str = ""
    birth_info: str = ""
    chart_type: str = ""
    strategy: str = ""
    strategy_desc: str = ""
    authority: str = ""
    authority_desc: str = ""
    profile: str = ""
    profile_desc: str = ""
    signature: str = ""
    not_self: str = ""
    manifestation_style: str = ""
    manifestation_desc: str = ""
    defined_centers: list = []
    undefined_centers: list = []
    channels: list = []
    gates: list = []
    type_desc: str = ""

@app.post("/generate-pdf")
def generate_pdf(req: PDFChartRequest):
    try:
        buffer = io.BytesIO()

        # Brand colors
        teal       = HexColor("#3D7A7A")
        teal_light = HexColor("#A8C8D8")
        text_dark  = HexColor("#2C3E35")
        text_mid   = HexColor("#5A6B5E")
        linen      = HexColor("#F0EDE8")
        linen_dark = HexColor("#E5E0D8")
        card_bg    = HexColor("#FFFFFF")

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18*mm,
            leftMargin=18*mm,
            topMargin=18*mm,
            bottomMargin=18*mm,
        )

        # Styles
        title_s   = ParagraphStyle("title",   fontName="Helvetica-Bold", fontSize=20, textColor=teal,      spaceAfter=2*mm)
        info_s    = ParagraphStyle("info",    fontName="Helvetica",      fontSize=8,  textColor=text_mid,  spaceAfter=5*mm)
        sec_s     = ParagraphStyle("sec",     fontName="Helvetica-Bold", fontSize=11, textColor=teal,      spaceAfter=2*mm, spaceBefore=2*mm)
        sub_s     = ParagraphStyle("sub",     fontName="Helvetica",      fontSize=8,  textColor=text_mid,  spaceAfter=3*mm)
        label_s   = ParagraphStyle("label",   fontName="Helvetica",      fontSize=8,  textColor=text_mid,  spaceAfter=1*mm)
        value_s   = ParagraphStyle("value",   fontName="Helvetica-Bold", fontSize=11, textColor=text_dark, spaceAfter=1*mm)
        desc_s    = ParagraphStyle("desc",    fontName="Helvetica",      fontSize=9,  textColor=text_dark, spaceAfter=4*mm, leading=13)
        cname_s   = ParagraphStyle("cname",   fontName="Helvetica-Bold", fontSize=10, textColor=teal,      spaceAfter=1*mm)
        cgift_s   = ParagraphStyle("cgift",   fontName="Helvetica-Bold", fontSize=7,  textColor=teal_light,spaceAfter=2*mm)
        cdesc_s   = ParagraphStyle("cdesc",   fontName="Helvetica",      fontSize=9,  textColor=text_dark, spaceAfter=4*mm, leading=13)
        gate_s    = ParagraphStyle("gate",    fontName="Helvetica",      fontSize=9,  textColor=text_dark, spaceAfter=2*mm, leading=13)
        footer_s  = ParagraphStyle("footer",  fontName="Helvetica",      fontSize=7,  textColor=text_mid,  alignment=TA_CENTER, spaceBefore=4*mm)

        story = []

        # ── Title ──
        story.append(Paragraph(f"{req.name}'s Human Design Chart", title_s))
        story.append(Paragraph(req.birth_info, info_s))
        story.append(HRFlowable(width="100%", thickness=1.5, color=teal, spaceAfter=5*mm))

        # ── Helper: section header ──
        def section(title, subtitle=None):
            story.append(Paragraph(title, sec_s))
            story.append(HRFlowable(width="100%", thickness=1, color=linen_dark, spaceAfter=3*mm))
            if subtitle:
                story.append(Paragraph(subtitle, sub_s))

        # ── Helper: summary item ──
        def summary_item(label, value, desc=""):
            items = [Paragraph(label, label_s), Paragraph(value, value_s)]
            if desc:
                items.append(Paragraph(desc, desc_s))
            else:
                items.append(Spacer(1, 2*mm))
            items.append(HRFlowable(width="100%", thickness=0.5, color=linen_dark, spaceAfter=2*mm))
            story.extend(items)

        # ── Helper: center item ──
        def center_item(name, gift, desc):
            story.append(Paragraph(name, cname_s))
            story.append(Paragraph(gift.upper(), cgift_s))
            story.append(Paragraph(desc, cdesc_s))
            story.append(HRFlowable(width="100%", thickness=0.5, color=linen_dark, spaceAfter=2*mm))

        # Chart Summary
        section("Chart Summary")
        summary_item("Type — Your divine innate gifts and the foundation of how you operate best.", req.chart_type, req.type_desc)
        summary_item("Strategy — How you make things happen.", req.strategy, req.strategy_desc)
        summary_item("Inner Authority — How you make decisions best.", req.authority, req.authority_desc)
        summary_item("Profile — Layers of your personality.", req.profile, req.profile_desc)
        summary_item("Signature — A feeling that you are aligned.", req.signature)
        summary_item("Not-Self Theme — A feeling you get when you are misaligned and something is off.", req.not_self)
        summary_item("Manifestation Style", req.manifestation_style, req.manifestation_desc)

        # Defined Centers
        story.append(Spacer(1, 3*mm))
        section("Your Defined Centers", "Centers are like chakras, energy hubs in the body.")
        for c in req.defined_centers:
            center_item(c.get("name",""), c.get("gift",""), c.get("desc",""))

        # Undefined Centers
        story.append(Spacer(1, 3*mm))
        section("Your Undefined Centers", "Centers are like chakras, energy hubs in the body. These centers are open, so their energy ebbs and flows.")
        for c in req.undefined_centers:
            center_item(c.get("name",""), c.get("gift",""), c.get("desc",""))

        # Gates & Channels
        story.append(Spacer(1, 3*mm))
        section("Gates & Channels — Characteristics You Were Born With")

        for ch in req.channels:
            story.append(Paragraph(ch.get("name",""), cname_s))
            story.append(Paragraph(ch.get("desc",""), cdesc_s))
            story.append(HRFlowable(width="100%", thickness=0.5, color=linen_dark, spaceAfter=2*mm))

        if req.gates:
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph("Gates", cname_s))
            story.append(HRFlowable(width="100%", thickness=0.5, color=linen_dark, spaceAfter=2*mm))
            for g in req.gates:
                num = g.get("number","")
                desc = g.get("desc","")
                story.append(Paragraph(f"<b><font color='#3D7A7A'>{num}</font></b>  {desc}", gate_s))

        # Footer
        story.append(HRFlowable(width="100%", thickness=1, color=linen_dark, spaceBefore=4*mm, spaceAfter=2*mm))
        story.append(Paragraph("Generated by ROI of Peace · roiofpeace.com", footer_s))

        # Build with linen background
        def add_background(canvas, doc):
            canvas.saveState()
            canvas.setFillColor(linen)
            canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
            canvas.restoreState()

        doc.build(story, onFirstPage=add_background, onLaterPages=add_background)
        buffer.seek(0)

        filename = req.name.replace(" ", "-").lower() + "-human-design.pdf" if req.name else "human-design.pdf"
        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"status": "ROI of Peace Human Design API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
