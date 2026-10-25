import logging
from fastapi import APIRouter
from ..db import query
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["market"])

_CATALOG = "aiagenticdemo.stars_gold"

_ORG_MAP = {
    "H3312": "FLORIDA HEALTH CARE PLAN, INC.",
    "H5521": "COMMUNITY HEALTH CHOICE, INC.",
    "H2213": "BLUE SHIELD OF CALIFORNIA",
    "H6614": "KEYSTONE HEALTH PLAN EAST, INC.",
    "H7723": "EMPIRE HEALTHCHOICE ASSURANCE, INC.",
    "H8812": "BUCKEYE COMMUNITY HEALTH PLAN",
    "H9914": "MERCY CARE",
    "H1045": "WELLSTAR HEALTH SYSTEM",
    "H2156": "BLUE CROSS BLUE SHIELD OF ILLINOIS",
    "H3267": "BLUE CROSS AND BLUE SHIELD OF NC",
    "H4378": "PRIORITY HEALTH",
    "H5489": "PREMERA BLUE CROSS",
    "H6590": "ANTHEM HEALTHKEEPERS, INC.",
    "H7601": "ROCKY MOUNTAIN HEALTH PLANS",
}

_FALLBACK_ENROLLMENT = [
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2026, "enrollment": 95000},
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2022, "enrollment": 100200},
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2023, "enrollment": 105400},
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2024, "enrollment": 109800},
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2025, "enrollment": 112450},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2026, "enrollment": 82000},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2022, "enrollment": 86500},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2023, "enrollment": 90100},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2024, "enrollment": 94300},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2025, "enrollment": 98200},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2026, "enrollment": 115000},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2022, "enrollment": 120300},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2023, "enrollment": 125800},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2024, "enrollment": 130100},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2025, "enrollment": 134800},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2026, "enrollment": 55000},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2022, "enrollment": 58200},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2023, "enrollment": 61400},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2024, "enrollment": 64500},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2025, "enrollment": 67300},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2026, "enrollment": 74000},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2022, "enrollment": 78500},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2023, "enrollment": 82300},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2024, "enrollment": 85900},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2025, "enrollment": 89100},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2026, "enrollment": 44000},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2022, "enrollment": 46800},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2023, "enrollment": 49500},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2024, "enrollment": 52100},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2025, "enrollment": 54600},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2026, "enrollment": 60000},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2022, "enrollment": 63200},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2023, "enrollment": 66500},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2024, "enrollment": 69800},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2025, "enrollment": 72400},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2026, "enrollment": 34000},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2022, "enrollment": 36500},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2023, "enrollment": 38800},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2024, "enrollment": 41200},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2025, "enrollment": 43200},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2026, "enrollment": 50000},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2022, "enrollment": 53200},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2023, "enrollment": 56100},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2024, "enrollment": 59000},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2025, "enrollment": 61800},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2026, "enrollment": 38000},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2022, "enrollment": 40500},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2023, "enrollment": 43200},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2024, "enrollment": 46100},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2025, "enrollment": 48900},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2026, "enrollment": 45000},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2022, "enrollment": 47800},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2023, "enrollment": 50500},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2024, "enrollment": 53200},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2025, "enrollment": 55700},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2026, "enrollment": 30000},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2022, "enrollment": 32200},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2023, "enrollment": 34500},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2024, "enrollment": 36800},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2025, "enrollment": 38400},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2026, "enrollment": 35000},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2022, "enrollment": 37500},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2023, "enrollment": 39800},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2024, "enrollment": 42100},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2025, "enrollment": 44100},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2026, "enrollment": 48000},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2022, "enrollment": 50800},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2023, "enrollment": 53500},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2024, "enrollment": 56400},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2025, "enrollment": 59000},
]

_FALLBACK_PLAN_STARS = [
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2026, "overall_star": 3.5},
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2022, "overall_star": 3.5},
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2023, "overall_star": 4.0},
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2024, "overall_star": 4.0},
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "org_name": "FLORIDA HEALTH CARE PLAN, INC.", "state": "FL", "year": 2025, "overall_star": 4.0},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2026, "overall_star": 3.0},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2022, "overall_star": 3.0},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2023, "overall_star": 3.5},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2024, "overall_star": 3.5},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "org_name": "COMMUNITY HEALTH CHOICE, INC.", "state": "TX", "year": 2025, "overall_star": 3.5},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2026, "overall_star": 4.0},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2022, "overall_star": 4.5},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2023, "overall_star": 4.5},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2024, "overall_star": 4.5},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "org_name": "BLUE SHIELD OF CALIFORNIA", "state": "CA", "year": 2025, "overall_star": 4.5},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2026, "overall_star": 3.5},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2022, "overall_star": 4.0},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2023, "overall_star": 4.0},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2024, "overall_star": 4.0},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "org_name": "KEYSTONE HEALTH PLAN EAST, INC.", "state": "PA", "year": 2025, "overall_star": 4.0},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2026, "overall_star": 3.0},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2022, "overall_star": 3.5},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2023, "overall_star": 3.5},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2024, "overall_star": 3.5},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "org_name": "EMPIRE HEALTHCHOICE ASSURANCE, INC.", "state": "NY", "year": 2025, "overall_star": 4.0},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2026, "overall_star": 3.5},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2022, "overall_star": 4.0},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2023, "overall_star": 4.0},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2024, "overall_star": 4.0},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "org_name": "BUCKEYE COMMUNITY HEALTH PLAN", "state": "OH", "year": 2025, "overall_star": 4.0},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2026, "overall_star": 3.0},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2022, "overall_star": 3.0},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2023, "overall_star": 3.5},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2024, "overall_star": 3.5},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "org_name": "MERCY CARE", "state": "AZ", "year": 2025, "overall_star": 3.5},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2026, "overall_star": 2.5},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2022, "overall_star": 3.0},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2023, "overall_star": 3.0},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2024, "overall_star": 3.0},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "org_name": "WELLSTAR HEALTH SYSTEM", "state": "GA", "year": 2025, "overall_star": 3.5},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2026, "overall_star": 3.5},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2022, "overall_star": 4.0},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2023, "overall_star": 4.0},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2024, "overall_star": 4.0},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "org_name": "BLUE CROSS BLUE SHIELD OF ILLINOIS", "state": "IL", "year": 2025, "overall_star": 4.0},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2026, "overall_star": 3.5},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2022, "overall_star": 4.0},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2023, "overall_star": 4.0},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2024, "overall_star": 4.0},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "org_name": "BLUE CROSS AND BLUE SHIELD OF NC", "state": "NC", "year": 2025, "overall_star": 4.5},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2026, "overall_star": 3.0},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2022, "overall_star": 3.0},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2023, "overall_star": 3.5},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2024, "overall_star": 3.5},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "org_name": "PRIORITY HEALTH", "state": "MI", "year": 2025, "overall_star": 3.5},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2026, "overall_star": 4.0},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2022, "overall_star": 4.5},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2023, "overall_star": 4.5},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2024, "overall_star": 4.5},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "org_name": "PREMERA BLUE CROSS", "state": "WA", "year": 2025, "overall_star": 4.5},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2026, "overall_star": 3.5},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2022, "overall_star": 4.0},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2023, "overall_star": 4.0},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2024, "overall_star": 4.0},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "org_name": "ANTHEM HEALTHKEEPERS, INC.", "state": "VA", "year": 2025, "overall_star": 4.0},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2026, "overall_star": 3.5},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2022, "overall_star": 3.5},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2023, "overall_star": 4.0},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2024, "overall_star": 4.0},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "org_name": "ROCKY MOUNTAIN HEALTH PLANS", "state": "CO", "year": 2025, "overall_star": 4.0},
]


@router.get("/market/enrollment")
def market_enrollment():
    if not settings.databricks_host:
        logger.info("market_enrollment: no databricks_host, using fallback")
        return _FALLBACK_ENROLLMENT
    try:
        sql = f"""
            SELECT SUBSTRING(e.contract_id, 1, 5) as contract_id,
                   COALESCE(s.plan_name, e.contract_id) as plan_name,
                   COALESCE(s.org_name, e.contract_id) as org_name,
                   COALESCE(s.state, '') as state,
                   CAST(e.measurement_year AS INT) as year,
                   CAST(COALESCE(e.total_enrollment, 0) AS INT) as enrollment
            FROM {_CATALOG}.cms_plan_enrollment_history e
            LEFT JOIN (SELECT contract_id,
                              SUBSTRING(contract_id, 1, 5) as cid_short,
                              FIRST(plan_name) as plan_name,
                              FIRST(org_name) as org_name,
                              FIRST(state) as state
                       FROM {_CATALOG}.cms_plan_star_history
                       GROUP BY contract_id) s
              ON SUBSTRING(e.contract_id, 1, 5) = s.cid_short
              where e.measurement_year = 2026
            ORDER BY contract_id, e.measurement_year
        """
        logger.info("market_enrollment: executing query against %s.cms_plan_enrollment_history", _CATALOG)
        rows = query(sql)
        logger.info("market_enrollment: query returned %d rows", len(rows))
        if rows:
            return rows
        return []
    except Exception as exc:
        logger.error("market_enrollment DB query failed: %s", exc, exc_info=True)
    return []


@router.get("/market/plan-stars")
def market_plan_stars():
    if not settings.databricks_host:
        logger.info("market_plan_stars: no databricks_host, using fallback")
        return _FALLBACK_PLAN_STARS
    try:
        sql = f"""
            SELECT SUBSTRING(contract_id, 1, 5) as contract_id,
                   plan_name, org_name, state,
                   CAST(measurement_year AS INT) as year,
                   CAST(overall_star_rating AS DOUBLE) as overall_star
            FROM {_CATALOG}.cms_plan_star_history
            ORDER BY contract_id, measurement_year
        """
        logger.info("market_plan_stars: executing query against %s.cms_plan_star_history", _CATALOG)
        rows = query(sql)
        logger.info("market_plan_stars: query returned %d rows", len(rows))
        if rows:
            return rows
        return []
    except Exception as exc:
        logger.error("market_plan_stars DB query failed: %s", exc, exc_info=True)
    return []


@router.get("/market/measure-stars")
def market_measure_stars(contracts: str = ""):
    if not settings.databricks_host:
        logger.info("market_measure_stars: no databricks_host configured")
        return []
    if not contracts:
        logger.info("market_measure_stars: no contracts specified")
        return []

    cid_list = [c.strip() for c in contracts.split(",") if c.strip()]
    if not cid_list:
        return []
    # NOTE: previously truncated to 50 — anything past index 50 silently
    # dropped, which combined with per-contract frontend caching caused
    # affected contracts to permanently show as empty. Raised to 500;
    # frontend chunks requests in groups <= 400.
    placeholders = ",".join(f"'{c}'" for c in cid_list[:500])
    if len(cid_list) > 500:
        logger.warning("market_measure_stars: truncating %d contracts to 500", len(cid_list))

    _LOOKUP = "aiagenticdemo.stars_bronze"
    try:
        # INNER JOIN stars_measurelist so ONLY measures present in both tables
        # come through. Domain classification is driven by ml.Category (the
        # canonical mapping owned by the measurelist), not by m.domain codes.
        sql = f"""
            SELECT SUBSTRING(m.contract_id, 1, 5) as contract_id,
                   COALESCE(s.plan_name, m.org_name, m.contract_id) as plan_name,
                   COALESCE(m.org_name, s.org_name, m.contract_id) as org_name,
                   COALESCE(s.state, '') as state,
                   CAST(m.measurement_year AS INT) as year,
                   CASE
                       WHEN ml.Category LIKE 'Medication%' THEN 'Medical Adherence'
                       WHEN ml.Category LIKE 'CMS%Admin%'     THEN 'Admin'
                       WHEN ml.Category LIKE 'CAHPS%'         THEN 'CAHPS'
                       WHEN ml.Category LIKE 'HEDIS%'         THEN 'HEDIS'
                       WHEN ml.Category LIKE 'HOS%'           THEN 'HOS'
                       ELSE 'Admin'
                   END as domain,
                   m.measure_name,
                   CAST(m.star_rating AS DOUBLE) as star_rating,
                   1 as weight
            FROM {_CATALOG}.cms_measure_star_history m
            INNER JOIN (SELECT LOWER(TRIM(Measure)) as measure_key,
                               FIRST(TRIM(Category)) as Category
                        FROM {_LOOKUP}.stars_measurelist
                        GROUP BY LOWER(TRIM(Measure))) ml
              ON LOWER(TRIM(m.measure_name)) = ml.measure_key
            LEFT JOIN (SELECT contract_id,
                              SUBSTRING(contract_id, 1, 5) as cid_short,
                              FIRST(plan_name) as plan_name,
                              FIRST(org_name) as org_name, FIRST(state) as state
                       FROM {_CATALOG}.cms_plan_star_history GROUP BY contract_id) s
              ON SUBSTRING(m.contract_id, 1, 5) = s.cid_short
            WHERE m.measurement_year BETWEEN 2021 AND 2027
              AND SUBSTRING(m.contract_id, 1, 5) IN ({placeholders})
            ORDER BY contract_id, m.measurement_year, domain, m.measure_name
        """
        logger.info("market_measure_stars: querying for contracts: %s", contracts)
        rows = query(sql)
        logger.info("market_measure_stars: query returned %d rows", len(rows))
        if rows:
            result = [dict(r) if not isinstance(r, dict) else r for r in rows]
            logger.info("market_measure_stars: returning %d rows", len(result))
            return result
    except Exception as exc:
        logger.error("market_measure_stars DB query failed: %s", exc, exc_info=True)
    return []


_DOMAIN_MAP = {
    "HD": "HEDIS", "Part C": "HEDIS",
    "C": "CAHPS",
    "HOS": "HOS",
    "D": "Medical Adherence", "Drug": "Medical Adherence", "Part D": "Medical Adherence",
}


def _map_domain(raw: str) -> str:
    """Map Databricks domain codes like 'HD2 – Managing Chronic Conditions' to standard categories."""
    if not raw:
        return "Admin"
    raw_upper = raw.upper()
    if raw_upper.startswith("HD") or raw_upper.startswith("PART C"):
        return "HEDIS"
    if raw_upper.startswith("HOS"):
        return "HOS"
    if "CAHPS" in raw_upper:
        return "CAHPS"
    if raw_upper.startswith("DD") or raw_upper.startswith("D0") or raw_upper.startswith("D1") or "DRUG" in raw_upper or "ADHERENCE" in raw_upper or raw_upper.startswith("PART D"):
        return "Medical Adherence"
    return "Admin"


@router.get("/market/status")
def market_status():
    """Debug endpoint to check market data connectivity, column names, and contract_id formats."""
    from ..config import settings as s
    result = {
        "has_host": bool(s.databricks_host),
        "catalog": _CATALOG,
        "tables": {},
    }
    if not s.databricks_host:
        result["status"] = "no_config"
        return result
    tables = ["cms_plan_enrollment_history", "cms_plan_star_history", "cms_measure_star_history"]
    for tbl in tables:
        fqn = f"{_CATALOG}.{tbl}"
        try:
            sample = query(f"SELECT * FROM {fqn} LIMIT 1")
            cids = query(f"SELECT DISTINCT contract_id FROM {fqn} LIMIT 20")
            result["tables"][tbl] = {
                "columns": list(sample[0].keys()) if sample else "empty",
                "sample": sample[0] if sample else None,
                "contract_ids": [r["contract_id"] for r in cids] if cids else [],
                "row_count": query(f"SELECT COUNT(*) as n FROM {fqn}")[0]["n"],
            }
        except Exception as exc:
            result["tables"][tbl] = {"error": str(exc)[:200]}
    result["status"] = "connected"
    return result


def _gen_fallback_measures():
    import random
    random.seed(42)
    measures = {
        "HEDIS": [
            ("Breast Cancer Screening", 1), ("Colorectal Cancer Screening", 1), ("Diabetes Eye Exam", 1),
            ("Controlling Blood Pressure", 3), ("Hemoglobin A1c Control", 3), ("Medication Reconciliation", 1),
            ("Plan All-Cause Readmission", 3), ("Statin Therapy for CVD", 1), ("Osteoporosis Screening", 1),
            ("Follow-Up After ED Visit", 1),
        ],
        "CAHPS": [
            ("Getting Needed Care", 3), ("Getting Appointments Quickly", 3), ("Customer Service", 3),
            ("Rating of Health Plan", 3), ("Rating of Health Care", 1), ("Care Coordination", 1),
        ],
        "HOS": [
            ("Physical Health Outcomes", 3), ("Mental Health Outcomes", 3), ("Monitoring Physical Activity", 1),
        ],
        "Medical Adherence": [
            ("PDC Diabetes Medications", 3), ("PDC RAS Antagonists", 3), ("PDC Statins", 3),
        ],
        "Admin": [
            ("Appeals Auto-Forward", 1), ("Call Center Access", 3), ("Complaints per 1000", 1),
            ("CTM Complaints", 1), ("Member Enrollment", 1),
        ],
    }
    base_stars = {
        "H3312": {"HEDIS": 3.8, "CAHPS": 4.2, "HOS": 4.0, "Medical Adherence": 4.1, "Admin": 3.5},
        "H5521": {"HEDIS": 3.4, "CAHPS": 3.6, "HOS": 3.5, "Medical Adherence": 3.7, "Admin": 3.3},
        "H2213": {"HEDIS": 4.6, "CAHPS": 4.4, "HOS": 4.5, "Medical Adherence": 4.3, "Admin": 4.0},
        "H6614": {"HEDIS": 3.9, "CAHPS": 4.1, "HOS": 4.0, "Medical Adherence": 3.8, "Admin": 3.5},
        "H7723": {"HEDIS": 3.7, "CAHPS": 3.8, "HOS": 3.5, "Medical Adherence": 3.9, "Admin": 3.4},
        "H8812": {"HEDIS": 4.0, "CAHPS": 3.9, "HOS": 4.0, "Medical Adherence": 4.2, "Admin": 3.8},
        "H9914": {"HEDIS": 3.3, "CAHPS": 3.7, "HOS": 3.5, "Medical Adherence": 3.4, "Admin": 3.2},
        "H1045": {"HEDIS": 3.2, "CAHPS": 3.3, "HOS": 3.0, "Medical Adherence": 3.1, "Admin": 2.8},
        "H2156": {"HEDIS": 4.1, "CAHPS": 3.8, "HOS": 4.0, "Medical Adherence": 4.0, "Admin": 3.7},
        "H3267": {"HEDIS": 4.2, "CAHPS": 4.3, "HOS": 4.0, "Medical Adherence": 4.1, "Admin": 3.9},
        "H4378": {"HEDIS": 3.6, "CAHPS": 3.4, "HOS": 3.5, "Medical Adherence": 3.3, "Admin": 3.2},
        "H5489": {"HEDIS": 4.7, "CAHPS": 4.3, "HOS": 4.5, "Medical Adherence": 4.4, "Admin": 4.2},
        "H6590": {"HEDIS": 3.9, "CAHPS": 4.0, "HOS": 4.0, "Medical Adherence": 3.9, "Admin": 3.6},
        "H7601": {"HEDIS": 4.0, "CAHPS": 4.1, "HOS": 4.0, "Medical Adherence": 3.8, "Admin": 3.5},
    }
    contract_names = {r["contract_id"]: (r["plan_name"], r["org_name"], r["state"]) for r in _FALLBACK_PLAN_STARS}
    years = [2021,2022, 2023, 2024, 2025,2026,2027]
    rows = []
    for cid, dom_bases in base_stars.items():
        name, org, state = contract_names.get(cid, (cid, cid, ""))
        for domain, mlist in measures.items():
            for mname, weight in mlist:
                base = dom_bases.get(domain, 3.5)
                for yi, yr in enumerate(years):
                    drift = (yi - 2) * 0.08 * (1 if random.random() > 0.4 else -1)
                    noise = (random.random() - 0.5) * 0.6
                    star = min(5.0, max(1.0, round((base + drift + noise) * 2) / 2))
                    rows.append({
                        "contract_id": cid, "plan_name": name, "org_name": org, "state": state,
                        "year": yr, "domain": domain, "measure_name": mname,
                        "star_rating": star, "weight": weight,
                    })
    return rows
