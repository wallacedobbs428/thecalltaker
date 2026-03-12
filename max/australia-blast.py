#!/usr/bin/env python3
"""
AUSTRALIA BLAST — Overnight Cold Email Campaign
Feb 18, 2026

Creates contacts in GHL and sends cold Email 1 (Pain) to Australian AC companies.
Rate-limited to avoid GHL throttling. Sends ntfy updates.

Usage:
  python3 australia-blast.py
"""

import json
import sys
import os
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ===================================================
# CONFIG
# ===================================================

GHL_API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
GHL_LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
GHL_BASE = "https://services.leadconnectorhq.com"

NTFY_OPS_TOPIC = "tct-xK9mW4vR7pLd"
NTFY_WAR_TOPIC = "tct-warroom-Kx7mN9pQ"

FROM_EMAIL = "thecalltakerai@gmail.com"

BLAST_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BLAST_DIR, "australia-blast-log.txt")
STATE_FILE = os.path.join(BLAST_DIR, "australia-blast-state.json")

DELAY_BETWEEN_EMAILS = 8  # seconds between sends

# ===================================================
# LEADS — Australian Air Conditioning Companies
# ===================================================

AUSTRALIA_LEADS = [
    # === SYDNEY / NSW METRO ===
    {"firstName": "Peter", "companyName": "Sydmech Air Conditioning", "city": "Sydney", "state": "NSW", "email": "peter@sydmech.com.au"},
    {"firstName": "Ben", "companyName": "Ben Rafferty Air and Electrical", "city": "Sydney", "state": "NSW", "email": "Info@benraffertyair.com.au"},
    {"firstName": "Owner", "companyName": "Roberts Air Conditioning", "city": "Sydney", "state": "NSW", "email": "enquiries@robertsairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Air Cooling Sydney", "city": "Sydney", "state": "NSW", "email": "info@aircooling.com.au"},
    {"firstName": "Owner", "companyName": "Jay's Air Conditioning", "city": "Sydney", "state": "NSW", "email": "comfort@jaysair.com.au"},
    {"firstName": "Adam", "companyName": "Penrith Air Supply", "city": "Penrith", "state": "NSW", "email": "reception@penrithair.com.au"},
    {"firstName": "Owner", "companyName": "Enercell Air Conditioning", "city": "Sydney", "state": "NSW", "email": "info@enercellairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "All Climates Air Conditioning", "city": "Sydney", "state": "NSW", "email": "info@allclimates.com.au"},
    {"firstName": "Owner", "companyName": "Hero Air Conditioning", "city": "Parramatta", "state": "NSW", "email": "info@heroairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "All General Air", "city": "Sydney", "state": "NSW", "email": "enquiries@allgeneralair.com.au"},
    {"firstName": "Owner", "companyName": "Dream Air Conditioning", "city": "Sydney", "state": "NSW", "email": "info@dreamairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Northern Beaches Air", "city": "Sydney", "state": "NSW", "email": "sales@northernbeachesair.com.au"},
    {"firstName": "Tim", "companyName": "Alpine Air and Electrical", "city": "Sydney", "state": "NSW", "email": "tim@alpineairandelectrical.com.au"},
    {"firstName": "Owner", "companyName": "Frozone Air Conditioning", "city": "Sydney", "state": "NSW", "email": "service@frozoneair.com.au"},
    {"firstName": "Owner", "companyName": "New Wave Air Conditioning", "city": "Sydney", "state": "NSW", "email": "info@newwaveair.com.au"},
    {"firstName": "Owner", "companyName": "Waratah Air Conditioning", "city": "Sydney", "state": "NSW", "email": "sales@waratahair.com.au"},
    {"firstName": "Owner", "companyName": "Shire Air Conditioning", "city": "Sydney", "state": "NSW", "email": "admin@shireair.com.au"},
    {"firstName": "Owner", "companyName": "Alliance Climate Control", "city": "Sydney", "state": "NSW", "email": "admin@alliancecc.com.au"},
    {"firstName": "Owner", "companyName": "Eastern Air Conditioning", "city": "Sydney", "state": "NSW", "email": "admin@easternairconditioning.com.au"},
    {"firstName": "Jim", "companyName": "Innovation Air Conditioning", "city": "Sydney", "state": "NSW", "email": "jim@innovationaircon.com.au"},
    {"firstName": "Owner", "companyName": "KYC Air Conditioning", "city": "Sydney", "state": "NSW", "email": "enquiries@kycair.com.au"},
    {"firstName": "Owner", "companyName": "Ready Electrical", "city": "Sydney", "state": "NSW", "email": "office@readyelectrical.com.au"},

    # === NEWCASTLE / CENTRAL COAST / HUNTER ===
    {"firstName": "Owner", "companyName": "Xcel Air", "city": "Newcastle", "state": "NSW", "email": "xcelair@bigpond.net.au"},
    {"firstName": "Owner", "companyName": "East Coast Air", "city": "Newcastle", "state": "NSW", "email": "eca@eastcoastair.net.au"},
    {"firstName": "Michael", "companyName": "Nova Air Conditioning", "city": "Newcastle", "state": "NSW", "email": "admin@novaair.com.au"},
    {"firstName": "Owner", "companyName": "FernAir", "city": "Newcastle", "state": "NSW", "email": "sales@fernair.com.au"},
    {"firstName": "Owner", "companyName": "Ocean Breeze Air", "city": "Central Coast", "state": "NSW", "email": "admin@oceanbreezeair.com.au"},
    {"firstName": "Owner", "companyName": "Lakeside Air and Electrical", "city": "Lake Macquarie", "state": "NSW", "email": "office@lakesideair.com.au"},
    {"firstName": "Owner", "companyName": "Coolrite Air Conditioning", "city": "Newcastle", "state": "NSW", "email": "info@coolrite.com.au"},

    # === WOLLONGONG / ILLAWARRA ===
    {"firstName": "Owner", "companyName": "Airserve Air Conditioning", "city": "Wollongong", "state": "NSW", "email": "sales@airserve.com.au"},
    {"firstName": "Steve", "companyName": "Steve's Air Conditioning", "city": "Wollongong", "state": "NSW", "email": "steve@stevesairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Rapidcool Air Conditioning", "city": "Dapto", "state": "NSW", "email": "sales@rapidcool.com.au"},
    {"firstName": "Owner", "companyName": "Airdale Services", "city": "Wollongong", "state": "NSW", "email": "info@airdaleservices.com.au"},
    {"firstName": "Owner", "companyName": "Hott Air Conditioning", "city": "Wollongong", "state": "NSW", "email": "info@hottelectrics.com.au"},

    # === REGIONAL NSW ===
    {"firstName": "Owner", "companyName": "Chill-Rite Refrigeration", "city": "Dubbo", "state": "NSW", "email": "contact@chill-rite.com.au"},
    {"firstName": "Owner", "companyName": "Coffs Harbour Refrigeration", "city": "Coffs Harbour", "state": "NSW", "email": "service@coffsrefrigeration.com.au"},
    {"firstName": "Brett", "companyName": "Bathurst Air Conditioning", "city": "Bathurst", "state": "NSW", "email": "brett@bathurstairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Northernair", "city": "Lismore", "state": "NSW", "email": "info@northernair.com.au"},
    {"firstName": "Owner", "companyName": "Coolectrics", "city": "Wagga Wagga", "state": "NSW", "email": "info@coolectrics.com.au"},
    {"firstName": "Owner", "companyName": "AJM Air Conditioning", "city": "Lismore", "state": "NSW", "email": "office@ajmaircon.com.au"},
    {"firstName": "Owner", "companyName": "Armidale Air Conditioning", "city": "Armidale", "state": "NSW", "email": "admin@armidaleair.com.au"},
    {"firstName": "Owner", "companyName": "Energy Air Service", "city": "Port Macquarie", "state": "NSW", "email": "admin@energyair.net.au"},
    {"firstName": "Owner", "companyName": "Lawson Air Conditioning", "city": "Port Macquarie", "state": "NSW", "email": "sales@lawsonair.com.au"},
    {"firstName": "Owner", "companyName": "North West Heating Cooling", "city": "Armidale", "state": "NSW", "email": "office@northwesthc.com.au"},
    {"firstName": "Owner", "companyName": "Artisan Air", "city": "Byron Bay", "state": "NSW", "email": "hello@artisanair.com.au"},

    # === ALBURY / WODONGA / RIVERINA ===
    {"firstName": "Owner", "companyName": "Aircom Air Conditioning", "city": "Albury", "state": "NSW", "email": "aircom@aircom.net.au"},
    {"firstName": "Glenn", "companyName": "Custom Air Albury", "city": "Albury", "state": "NSW", "email": "glenn@customairalbury.com.au"},
    {"firstName": "Owner", "companyName": "Lopez Refrigeration", "city": "Albury", "state": "NSW", "email": "info@lopezaircon.com.au"},
    {"firstName": "Owner", "companyName": "BJ Heating and Cooling", "city": "Albury", "state": "NSW", "email": "admin@bjheatcool.com.au"},
    {"firstName": "Owner", "companyName": "Border Heating and Cooling", "city": "Albury", "state": "NSW", "email": "reception@borderheatingandcooling.com.au"},
    {"firstName": "Owner", "companyName": "Watters Electrical", "city": "Albury", "state": "NSW", "email": "albury@watters.com.au"},
    {"firstName": "Owner", "companyName": "Border Gas and Plumbing", "city": "Albury", "state": "NSW", "email": "bordergas@bigpond.com"},

    # === MELBOURNE / VIC METRO ===
    {"firstName": "Matt", "companyName": "Airfit Air Conditioning", "city": "Melbourne", "state": "VIC", "email": "matt@airfit.com.au"},
    {"firstName": "Owner", "companyName": "ACSM Melbourne", "city": "Melbourne", "state": "VIC", "email": "info@acsm.net.au"},
    {"firstName": "Owner", "companyName": "Service Air Conditioning Melbourne", "city": "Melbourne", "state": "VIC", "email": "info@sacm.com.au"},
    {"firstName": "Daniel", "companyName": "Melbourne HVAC Services", "city": "Melbourne", "state": "VIC", "email": "Daniel@mhvacs.com.au"},
    {"firstName": "Owner", "companyName": "Peninsula Heating and Cooling", "city": "Mornington", "state": "VIC", "email": "info@phacs.com.au"},
    {"firstName": "Owner", "companyName": "All Aspects Heating and Cooling", "city": "Melbourne", "state": "VIC", "email": "info@allaspectsheatcool.com.au"},
    {"firstName": "Owner", "companyName": "Mornington Peninsula Services", "city": "Mornington", "state": "VIC", "email": "info@morningtonpeninsulaservices.com.au"},
    {"firstName": "Owner", "companyName": "Metrocool", "city": "Werribee", "state": "VIC", "email": "admin@metrocool.com.au"},
    {"firstName": "Owner", "companyName": "Specialized Heating and Cooling", "city": "Melbourne", "state": "VIC", "email": "sales@specair.com.au"},
    {"firstName": "Owner", "companyName": "North West Air Conditioning", "city": "Melbourne", "state": "VIC", "email": "enquiries@nwac.com.au"},
    {"firstName": "Owner", "companyName": "Superior Heating and Cooling", "city": "Werribee", "state": "VIC", "email": "info@superiorhc.com.au"},
    {"firstName": "Ricky", "companyName": "Western Air Conditioning", "city": "Melbourne", "state": "VIC", "email": "ricky@westernairconditioning.com.au"},
    {"firstName": "Nick", "companyName": "Ackland Air and Electrics", "city": "Melbourne", "state": "VIC", "email": "nick@acklandairelec.com"},
    {"firstName": "Owner", "companyName": "Climatise", "city": "Melbourne", "state": "VIC", "email": "sales@climatise.com.au"},

    # === REGIONAL VICTORIA ===
    {"firstName": "Owner", "companyName": "White Swan Services", "city": "Ballarat", "state": "VIC", "email": "admin@whiteswanservices.com.au"},
    {"firstName": "Owner", "companyName": "BenAir Plumbing and HVAC", "city": "Bendigo", "state": "VIC", "email": "sales@benair.com.au"},
    {"firstName": "Owner", "companyName": "Bendigo Refrigeration", "city": "Bendigo", "state": "VIC", "email": "admin@bracs.com.au"},
    {"firstName": "Owner", "companyName": "GJ Bradding Heating and Cooling", "city": "Geelong", "state": "VIC", "email": "reception@gjbradding.com.au"},
    {"firstName": "Owner", "companyName": "Upside Down Air Conditioning", "city": "Geelong", "state": "VIC", "email": "bookings@upsidedownairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Bellarine Refrigeration", "city": "Geelong", "state": "VIC", "email": "sales@bellarinerefrigeration.com.au"},

    # === BRISBANE / QLD METRO ===
    {"firstName": "Owner", "companyName": "Acer Services", "city": "Brisbane", "state": "QLD", "email": "enquiries@acerservices.com.au"},
    {"firstName": "Owner", "companyName": "Amended Air", "city": "Brisbane", "state": "QLD", "email": "info@amendedair.com.au"},
    {"firstName": "Owner", "companyName": "AC Brisbane", "city": "Brisbane", "state": "QLD", "email": "info@acbrisbane.com.au"},
    {"firstName": "Owner", "companyName": "Shelair Commercial AC", "city": "Brisbane", "state": "QLD", "email": "info@shelair.com.au"},
    {"firstName": "Owner", "companyName": "Air Conditioning Solutions", "city": "Brisbane", "state": "QLD", "email": "info@airconditioningsolutions.com.au"},
    {"firstName": "Owner", "companyName": "Sparkrite Electrical", "city": "Brisbane", "state": "QLD", "email": "spark_rite@bigpond.com"},
    {"firstName": "Owner", "companyName": "Advanced Climate Solutions", "city": "Brisbane", "state": "QLD", "email": "info@advancedclimatesolutions.com.au"},
    {"firstName": "Owner", "companyName": "Swind Air Conditioning", "city": "Brisbane", "state": "QLD", "email": "admin@swind.com.au"},
    {"firstName": "Daniel", "companyName": "Crown Power Air Conditioning", "city": "Brisbane", "state": "QLD", "email": "daniel@crownpower.com.au"},
    {"firstName": "Owner", "companyName": "AC Plus Brisbane", "city": "Brisbane", "state": "QLD", "email": "admin@acplusbrisbane.com.au"},
    {"firstName": "Owner", "companyName": "RNR Air Conditioning", "city": "Caboolture", "state": "QLD", "email": "info@rnrairconditioning.com.au"},
    {"firstName": "Darryl", "companyName": "Supercool QLD", "city": "Brisbane", "state": "QLD", "email": "darryl@supercoolqld.com.au"},
    {"firstName": "Owner", "companyName": "Ice Blast Air Conditioning", "city": "Brisbane", "state": "QLD", "email": "info@iceblast.com.au"},
    {"firstName": "Owner", "companyName": "Thompson Cooling", "city": "Brisbane", "state": "QLD", "email": "admin@thompsoncooling.com.au"},

    # === GOLD COAST / SUNSHINE COAST ===
    {"firstName": "Owner", "companyName": "The Cool Shop", "city": "Sunshine Coast", "state": "QLD", "email": "info@thecoolshop.com.au"},
    {"firstName": "Owner", "companyName": "Acclaim Air Conditioning", "city": "Gold Coast", "state": "QLD", "email": "info@acclaimair.com.au"},
    {"firstName": "Owner", "companyName": "Master Aircon", "city": "Gold Coast", "state": "QLD", "email": "info@masteraircon.com.au"},
    {"firstName": "Owner", "companyName": "Think Cooling", "city": "Gold Coast", "state": "QLD", "email": "reception@thinkcooling.com.au"},
    {"firstName": "Anthony", "companyName": "Cool Air Conditioning", "city": "Sunshine Coast", "state": "QLD", "email": "anthony@coolaircon.com.au"},
    {"firstName": "Owner", "companyName": "Allchin Airconditioning", "city": "Sunshine Coast", "state": "QLD", "email": "admin@allchinairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Davies Refrigeration", "city": "Sunshine Coast", "state": "QLD", "email": "daviesair@gmail.com"},

    # === REGIONAL QLD ===
    {"firstName": "Owner", "companyName": "ACR Solutions", "city": "Toowoomba", "state": "QLD", "email": "info@acrsolutions.com.au"},
    {"firstName": "Owner", "companyName": "Air Conditioning Queensland", "city": "Toowoomba", "state": "QLD", "email": "getcool@airconditioningqueensland.com.au"},
    {"firstName": "Owner", "companyName": "Alpine Refrigeration", "city": "Toowoomba", "state": "QLD", "email": "sales@alpinerefrigeration.com.au"},
    {"firstName": "Owner", "companyName": "Superior HVAC", "city": "Toowoomba", "state": "QLD", "email": "service@shvac.com.au"},
    {"firstName": "Daymon", "companyName": "Mason's Air Conditioning", "city": "Toowoomba", "state": "QLD", "email": "daymon@masonsaircon.com.au"},
    {"firstName": "Owner", "companyName": "Enterprise Air", "city": "Bundaberg", "state": "QLD", "email": "admin@enterpriseair.com.au"},
    {"firstName": "Owner", "companyName": "Air Mr Refrigeration", "city": "Hervey Bay", "state": "QLD", "email": "airmr.refrigeration@outlook.com"},
    {"firstName": "Owner", "companyName": "Arctic Cold Refrigeration", "city": "Hervey Bay", "state": "QLD", "email": "info@arcticcold.com.au"},
    {"firstName": "Gordon", "companyName": "Irving Refrigeration", "city": "Bundaberg", "state": "QLD", "email": "gordonirving1980@gmail.com"},

    # === CAIRNS / NORTH QUEENSLAND ===
    {"firstName": "Jace", "companyName": "Cairns AC and Refrigeration", "city": "Cairns", "state": "QLD", "email": "cairnsfridgy@gmail.com"},
    {"firstName": "Owner", "companyName": "Alphacool", "city": "Cairns", "state": "QLD", "email": "admin@alphacool.com.au"},
    {"firstName": "Owner", "companyName": "Ice Ice Baby Air", "city": "Cairns", "state": "QLD", "email": "info@iceicebabyair.com.au"},
    {"firstName": "Owner", "companyName": "Integral Electrics QLD", "city": "Cairns", "state": "QLD", "email": "admin@integralelectricsqld.com.au"},
    {"firstName": "Owner", "companyName": "Northern Air Repair", "city": "Cairns", "state": "QLD", "email": "admin@nar.net.au"},
    {"firstName": "Owner", "companyName": "Ample Electrical", "city": "Cairns", "state": "QLD", "email": "ampleelectrical@bigpond.com"},

    # === TOWNSVILLE ===
    {"firstName": "Owner", "companyName": "DMC Electrical and Air", "city": "Townsville", "state": "QLD", "email": "info@dmctownsville.com.au"},
    {"firstName": "Owner", "companyName": "Townsville Air Conditioning", "city": "Townsville", "state": "QLD", "email": "admin@townsvilleaircon.com.au"},
    {"firstName": "Owner", "companyName": "SIC Airconditioning", "city": "Townsville", "state": "QLD", "email": "info@sicair.com.au"},
    {"firstName": "Owner", "companyName": "Polar Industries", "city": "Townsville", "state": "QLD", "email": "reception@polarindustries.com.au"},
    {"firstName": "Owner", "companyName": "Law Air Conditioning", "city": "Townsville", "state": "QLD", "email": "lawairconditioning@gmail.com"},

    # === PERTH / WA METRO ===
    {"firstName": "Owner", "companyName": "Leading Air", "city": "Perth", "state": "WA", "email": "info@leadingair.com.au"},
    {"firstName": "Owner", "companyName": "Total Air Conditioning", "city": "Perth", "state": "WA", "email": "service@totalairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Commercial Air Solutions", "city": "Perth", "state": "WA", "email": "service@comair.com.au"},
    {"firstName": "Ben", "companyName": "RCD Electrical Perth", "city": "Perth", "state": "WA", "email": "ben@rcdelectricalperth.com.au"},
    {"firstName": "Owner", "companyName": "Aircon Perth", "city": "Perth", "state": "WA", "email": "info@airconperth.com"},
    {"firstName": "Owner", "companyName": "Westwide Air Conditioning", "city": "Perth", "state": "WA", "email": "info@westwideaircon.com.au"},
    {"firstName": "Owner", "companyName": "WestOz Trades", "city": "Perth", "state": "WA", "email": "admin@westoztrades.com.au"},
    {"firstName": "Owner", "companyName": "Ford and Doonan", "city": "Bunbury", "state": "WA", "email": "bunbury@fdair.com.au"},

    # === REGIONAL WA ===
    {"firstName": "Owner", "companyName": "Alliance Air Conditioning WA", "city": "Mandurah", "state": "WA", "email": "sales@allianceairconwa.com.au"},
    {"firstName": "Owner", "companyName": "iBreeze Air Conditioning", "city": "Mandurah", "state": "WA", "email": "admin@ibreeze.com.au"},
    {"firstName": "Phil", "companyName": "Remote Air Solutions", "city": "Rockingham", "state": "WA", "email": "phil@remoteairsolutions.com.au"},
    {"firstName": "Owner", "companyName": "JFK Electrical and Air", "city": "Mandurah", "state": "WA", "email": "info@jfkelectrical.com.au"},

    # === ADELAIDE / SA ===
    {"firstName": "Owner", "companyName": "Affordair", "city": "Adelaide", "state": "SA", "email": "aircon@affordair.com.au"},
    {"firstName": "Owner", "companyName": "Everything Air Conditioning", "city": "Adelaide", "state": "SA", "email": "info@everythingairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Acer Air Adelaide", "city": "Adelaide", "state": "SA", "email": "admin@acerair.com.au"},
    {"firstName": "Owner", "companyName": "All Seasons Air Conditioning", "city": "Adelaide", "state": "SA", "email": "sales@allseasonsair.com.au"},

    # === CANBERRA / ACT ===
    {"firstName": "Owner", "companyName": "Air Conditioning Canberra", "city": "Canberra", "state": "ACT", "email": "info@airconditioningcbr.com.au"},

    # === HOBART / TASMANIA ===
    {"firstName": "Owner", "companyName": "The Heat Pump Man", "city": "Hobart", "state": "TAS", "email": "theheatpumpman@bigpond.com"},
    {"firstName": "Owner", "companyName": "Parr Air", "city": "Hobart", "state": "TAS", "email": "service@parrair.com.au"},
    {"firstName": "Owner", "companyName": "TCM Mechanical", "city": "Hobart", "state": "TAS", "email": "office@tcmpl.com.au"},
    {"firstName": "Owner", "companyName": "Tas Heating and Cooling", "city": "Launceston", "state": "TAS", "email": "info@tasheatingandcooling.com.au"},
    {"firstName": "Owner", "companyName": "Unimech Tasmania", "city": "Launceston", "state": "TAS", "email": "info@unimechtas.com.au"},
    {"firstName": "Owner", "companyName": "WMcA Refrigeration", "city": "Hobart", "state": "TAS", "email": "admin@wmca.com.au"},

    # === DARWIN / NT ===
    {"firstName": "Owner", "companyName": "Airducter", "city": "Darwin", "state": "NT", "email": "reception@airducter.com.au"},
    {"firstName": "Owner", "companyName": "Service Air NT", "city": "Darwin", "state": "NT", "email": "accounts@serviceair.com.au"},
    {"firstName": "Owner", "companyName": "Pro Cool NT", "city": "Darwin", "state": "NT", "email": "procoolnt@gmail.com"},
    {"firstName": "Owner", "companyName": "Top End RACE", "city": "Darwin", "state": "NT", "email": "admin@topendrace.com.au"},
    {"firstName": "Owner", "companyName": "Active Airconz", "city": "Darwin", "state": "NT", "email": "admin@airconz.com"},
    {"firstName": "Owner", "companyName": "UB Cool", "city": "Darwin", "state": "NT", "email": "sales@ubcool.com.au"},
    {"firstName": "Owner", "companyName": "Sam Eyles Refrigeration NT", "city": "Darwin", "state": "NT", "email": "admin@sernt.com.au"},
    {"firstName": "Owner", "companyName": "Johnny Cool", "city": "Darwin", "state": "NT", "email": "admin@johnnycool.com.au"},
    {"firstName": "Owner", "companyName": "Top End Air Conditioning", "city": "Darwin", "state": "NT", "email": "sales@teamnt.com.au"},
    {"firstName": "Owner", "companyName": "The Cool Guys NT", "city": "Darwin", "state": "NT", "email": "office@coolguysnt.com.au"},

    # === ALICE SPRINGS / CENTRAL AUSTRALIA ===
    {"firstName": "Owner", "companyName": "Steve Electrix", "city": "Alice Springs", "state": "NT", "email": "office@steveselectrix.com.au"},
    {"firstName": "Owner", "companyName": "Emperor Refrigeration", "city": "Alice Springs", "state": "NT", "email": "info@emperorrefrigeration.com.au"},
    {"firstName": "Owner", "companyName": "CKS Electrical and AC", "city": "Alice Springs", "state": "NT", "email": "orders@ckselectrical.com.au"},

    # === WAVE 2 — ADDITIONAL LEADS ===

    # Sydney Wave 2
    {"firstName": "Owner", "companyName": "Frost Air Conditioning", "city": "Castle Hill", "state": "NSW", "email": "sales@frostair.com.au"},
    {"firstName": "Owner", "companyName": "Proven Air Conditioning", "city": "Sydney", "state": "NSW", "email": "info@provenair.com.au"},
    {"firstName": "Owner", "companyName": "Brennan Air Conditioning", "city": "Castle Hill", "state": "NSW", "email": "brennanair@bigpond.com"},
    {"firstName": "Owner", "companyName": "Hills Air Conditioning", "city": "North Ryde", "state": "NSW", "email": "info@hillsair.com.au"},
    {"firstName": "Owner", "companyName": "Oregan Air Conditioning", "city": "Kenthurst", "state": "NSW", "email": "sales@oreganair.com.au"},

    # Melbourne Wave 2
    {"firstName": "Owner", "companyName": "ExtrordinAir", "city": "Melbourne", "state": "VIC", "email": "sales@extrordinair.com.au"},
    {"firstName": "Owner", "companyName": "Barrcon Air Conditioning", "city": "Croydon", "state": "VIC", "email": "service@barrcon.com.au"},
    {"firstName": "Owner", "companyName": "Advanced Heating and Cooling", "city": "Melbourne", "state": "VIC", "email": "enquiries@advancehc.com.au"},
    {"firstName": "Owner", "companyName": "Maroondah Heating and Cooling", "city": "Bayswater", "state": "VIC", "email": "Sales@maroondahair.com.au"},

    # Brisbane Wave 2
    {"firstName": "Owner", "companyName": "Sun City Air", "city": "Brisbane", "state": "QLD", "email": "suncityair@suncityair.com.au"},
    {"firstName": "Owner", "companyName": "CoolTimes Services", "city": "Brisbane", "state": "QLD", "email": "enquiries@cooltimes.com.au"},
    {"firstName": "Owner", "companyName": "Marsh Air", "city": "Brisbane", "state": "QLD", "email": "admin@marshair.com"},
    {"firstName": "Owner", "companyName": "Dawson Electric and Air", "city": "Brisbane", "state": "QLD", "email": "info@dawsonelectric.com.au"},
    {"firstName": "Owner", "companyName": "Fused Air", "city": "Brisbane", "state": "QLD", "email": "admin@fusedair.com.au"},

    # Perth Wave 2
    {"firstName": "Owner", "companyName": "Mouritz Air Conditioning", "city": "Perth", "state": "WA", "email": "info@mouritz.com.au"},
    {"firstName": "Owner", "companyName": "Cyber Air Conditioning", "city": "Perth", "state": "WA", "email": "bookings@cyberairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "DACS Air Conditioning", "city": "Perth", "state": "WA", "email": "info@dacsair.com.au"},
    {"firstName": "Chris", "companyName": "Global Cool Air", "city": "Perth", "state": "WA", "email": "chrisglobalcooling@gmail.com"},

    # Adelaide Wave 2
    {"firstName": "Owner", "companyName": "Domestic AC Services SA", "city": "Adelaide", "state": "SA", "email": "admin@domestic-ac.com"},
    {"firstName": "Owner", "companyName": "M and R Air Conditioning", "city": "Adelaide", "state": "SA", "email": "admin@mandrairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "ABA Air Conditioning", "city": "Adelaide", "state": "SA", "email": "admin@abaairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "SISA Air Conditioning", "city": "Adelaide", "state": "SA", "email": "info@sisaairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Quick Fix Electrical and AC", "city": "Adelaide", "state": "SA", "email": "info@quickfixelectrical.com.au"},

    # Canberra Wave 2
    {"firstName": "Owner", "companyName": "Heating Cooling Services Canberra", "city": "Canberra", "state": "ACT", "email": "enquiry@hcscanberra.com.au"},
    {"firstName": "Owner", "companyName": "Canberra Mechanical Services", "city": "Canberra", "state": "ACT", "email": "admin@cmservices.net.au"},
    {"firstName": "Owner", "companyName": "Bell Air Canberra", "city": "Canberra", "state": "ACT", "email": "sales@bellair.com.au"},

    # === WAVE 3 — MORE LEADS ===

    # Geelong / Regional VIC Wave 3
    {"firstName": "Owner", "companyName": "Middletons Group", "city": "Geelong", "state": "VIC", "email": "sales@middletonsgroup.com.au"},
    {"firstName": "Owner", "companyName": "Climatic AC", "city": "Geelong", "state": "VIC", "email": "sales@climatic.com.au"},
    {"firstName": "Owner", "companyName": "Too Hot To Handle", "city": "Geelong", "state": "VIC", "email": "info@toohottohandle.com.au"},
    {"firstName": "Owner", "companyName": "Armstrong Air", "city": "Geelong", "state": "VIC", "email": "info@armstrongair.com.au"},
    {"firstName": "Owner", "companyName": "North West Geelong AC", "city": "Geelong", "state": "VIC", "email": "office@northwestgeelong.com.au"},
    {"firstName": "Owner", "companyName": "Belly's Air Conditioning", "city": "Geelong", "state": "VIC", "email": "belly@sunet.com.au"},

    # Penrith / Blue Mountains NSW Wave 3
    {"firstName": "Owner", "companyName": "Ample Air", "city": "Penrith", "state": "NSW", "email": "enquiries@ampleair.com.au"},
    {"firstName": "Owner", "companyName": "Lower Mountains AC", "city": "Penrith", "state": "NSW", "email": "info@lmac.com.au"},
    {"firstName": "Owner", "companyName": "Altitude Air Solutions", "city": "Blue Mountains", "state": "NSW", "email": "info@altitudeairsolutions.com.au"},
    {"firstName": "Owner", "companyName": "Preferred Air Conditioning", "city": "Penrith", "state": "NSW", "email": "preferredair@outlook.com"},
    {"firstName": "Owner", "companyName": "Beacon Air Service", "city": "Penrith", "state": "NSW", "email": "service@beaconair.com.au"},
    {"firstName": "Owner", "companyName": "West Air Conditioning", "city": "Penrith", "state": "NSW", "email": "sales@westair.com.au"},

    # Sunshine Coast QLD Wave 3
    {"firstName": "Owner", "companyName": "Gealy's Refrigeration", "city": "Sunshine Coast", "state": "QLD", "email": "admin@gealysrefrigeration.com"},
    {"firstName": "Owner", "companyName": "Luxair Air Conditioning", "city": "Sunshine Coast", "state": "QLD", "email": "admin@luxaircon.com.au"},
    {"firstName": "Jon", "companyName": "Noosa Refrigeration", "city": "Noosa", "state": "QLD", "email": "jon@nrac.com.au"},

    # Northern Perth WA Wave 3
    {"firstName": "Owner", "companyName": "Joondalup Air Conditioning", "city": "Perth", "state": "WA", "email": "admin@joondalupair.com.au"},
    {"firstName": "Owner", "companyName": "Aircond Installs WA", "city": "Perth", "state": "WA", "email": "mail@aircondinstallswa.com.au"},
    {"firstName": "Owner", "companyName": "NRS Refrigeration", "city": "Perth", "state": "WA", "email": "service@nrs.net.au"},

    # === WAVE 4 — EVEN MORE LEADS ===

    # Hunter Valley NSW
    {"firstName": "Owner", "companyName": "OnSite Air Conditioning", "city": "Maitland", "state": "NSW", "email": "ask@onsiteair.com.au"},
    {"firstName": "Owner", "companyName": "Valley Air Conditioning", "city": "Maitland", "state": "NSW", "email": "admin@valleyairconditioning.com.au"},
    {"firstName": "Owner", "companyName": "Chillax HVAC Services", "city": "Newcastle", "state": "NSW", "email": "admin@chillaxhvacservices.com.au"},

    # Shepparton / Goulburn Valley VIC
    {"firstName": "Owner", "companyName": "Dicksons Refrigeration", "city": "Shepparton", "state": "VIC", "email": "admin@dicksonsrefrigeration.com.au"},
    {"firstName": "Owner", "companyName": "GV Trade Group", "city": "Shepparton", "state": "VIC", "email": "admin@gvtradegroup.com.au"},
    {"firstName": "Owner", "companyName": "Arctic Refrigeration", "city": "Kyabram", "state": "VIC", "email": "info@arcticrefrigeration.com.au"},
    {"firstName": "Owner", "companyName": "McCluskey Heating and Cooling", "city": "Shepparton", "state": "VIC", "email": "Office@mccluskeyheatingandcooling.com.au"},
    {"firstName": "Owner", "companyName": "Future NRG", "city": "Shepparton", "state": "VIC", "email": "info@futurenrg.com.au"},

    # Regional South Australia
    {"firstName": "Owner", "companyName": "Hancock's Air Conditioning", "city": "Whyalla", "state": "SA", "email": "admin@hancocksare.com.au"},
    {"firstName": "Owner", "companyName": "McMullen Trades", "city": "Whyalla", "state": "SA", "email": "admin@mcmullentrades.com.au"},
    {"firstName": "Owner", "companyName": "Quantum Refrigeration", "city": "Whyalla", "state": "SA", "email": "admin@quantumrefrigeration.com.au"},

    # === WAVE 5 ===

    # SE Melbourne / Gippsland VIC
    {"firstName": "Owner", "companyName": "I Heat and Cool", "city": "Pakenham", "state": "VIC", "email": "sales@iheatandcool.com.au"},
    {"firstName": "Owner", "companyName": "Cranbourne Air Conditioning", "city": "Cranbourne", "state": "VIC", "email": "cranbourne.air@gmail.com"},
    {"firstName": "Owner", "companyName": "Traralgon Refrigeration", "city": "Traralgon", "state": "VIC", "email": "admin@trac3844.com.au"},
    {"firstName": "Owner", "companyName": "Gippsland Heating and Cooling", "city": "Traralgon", "state": "VIC", "email": "info@gippslandair.com.au"},

    # Logan / Brisbane South QLD
    {"firstName": "Owner", "companyName": "Airlock Services", "city": "Brisbane", "state": "QLD", "email": "Info@airlockservices.com.au"},
    {"firstName": "Owner", "companyName": "All Purpose Air Conditioning", "city": "Brisbane", "state": "QLD", "email": "enquiries@allpurposeairconditioning.com.au"},

    # Southern Perth WA
    {"firstName": "Owner", "companyName": "Aircon Express", "city": "Perth", "state": "WA", "email": "sales@airconexpress.com.au"},

    # === WAVE 6 ===

    # Tasmania
    {"firstName": "Owner", "companyName": "DJK Electrical and Air", "city": "Kingston", "state": "TAS", "email": "admin@djkelectricalair.com.au"},
    {"firstName": "Owner", "companyName": "PMC Electrical Devonport", "city": "Devonport", "state": "TAS", "email": "pmcelectrical@gmail.com"},

    # Sydney NSW
    {"firstName": "Owner", "companyName": "CB Climate Control", "city": "Sydney", "state": "NSW", "email": "info@cbclimate.com"},
    {"firstName": "Owner", "companyName": "Impact Air Solutions", "city": "Sydney", "state": "NSW", "email": "info@impactairsolutions.com.au"},

    # Gladstone / Central QLD
    {"firstName": "Owner", "companyName": "Gray Electrical and AC", "city": "Gladstone", "state": "QLD", "email": "admin@geac.net.au"},
    {"firstName": "Owner", "companyName": "ACES Gladstone", "city": "Gladstone", "state": "QLD", "email": "admin@acesgladstone.com.au"},
    {"firstName": "Owner", "companyName": "Davey Service and Maintenance", "city": "Gladstone", "state": "QLD", "email": "admin@dsmq.com.au"},

    # All Cool Industries (Logan/Brisbane)
    {"firstName": "Owner", "companyName": "All Cool Industries", "city": "Brisbane", "state": "QLD", "email": "service@allcool.com.au"},

    # === WAVE 7 ===

    # West Brisbane QLD
    {"firstName": "Owner", "companyName": "Technicool Air Conditioning", "city": "Brisbane", "state": "QLD", "email": "enquiries@technicool.com.au"},
    {"firstName": "Owner", "companyName": "Hewitt Trade Services", "city": "Brisbane", "state": "QLD", "email": "enquiries@hewitttradeservices.com.au"},
    {"firstName": "Owner", "companyName": "Western Suburbs RAC", "city": "Brisbane", "state": "QLD", "email": "wsrac@outlook.com"},
    {"firstName": "Owner", "companyName": "Entire Air Solutions", "city": "Brisbane", "state": "QLD", "email": "admin@entireairsolutions.com.au"},
    {"firstName": "Owner", "companyName": "Aeromac Air Conditioning", "city": "Brisbane", "state": "QLD", "email": "info@aeromac.com.au"},

    # Campbelltown / Macarthur NSW
    {"firstName": "Darren", "companyName": "Haven Air Conditioning", "city": "Campbelltown", "state": "NSW", "email": "darren@havenair.com.au"},
    {"firstName": "Owner", "companyName": "Arctic Air and Electrical", "city": "Camden", "state": "NSW", "email": "service@arcticac.com.au"},
    {"firstName": "Owner", "companyName": "Shear Comfort Air", "city": "Campbelltown", "state": "NSW", "email": "shearcomfortair@bigpond.com"},
    {"firstName": "Owner", "companyName": "Campbelltown Air Conditioning", "city": "Campbelltown", "state": "NSW", "email": "info@campbelltownairconditioning.com.au"},
    {"firstName": "Brendan", "companyName": "Top Gun Air Conditioning", "city": "Campbelltown", "state": "NSW", "email": "sales@topgunair.com.au"},

    # South West WA
    {"firstName": "Owner", "companyName": "Busselton Refrigeration", "city": "Busselton", "state": "WA", "email": "sales@busseltonair.com.au"},
    {"firstName": "Owner", "companyName": "Stinson Air South West", "city": "Busselton", "state": "WA", "email": "info@stinsonair.com.au"},

    # === WAVE 8 ===

    # Sunshine Coast QLD
    {"firstName": "Owner", "companyName": "Buderim Air", "city": "Buderim", "state": "QLD", "email": "buderimair@gmail.com"},
    {"firstName": "Owner", "companyName": "Comfort Solutions", "city": "Sunshine Coast", "state": "QLD", "email": "info@comfortsolutions.com.au"},

    # Melbourne East VIC
    {"firstName": "Owner", "companyName": "NK Air", "city": "Melbourne", "state": "VIC", "email": "contact@nkair.com.au"},

    # Central Coast NSW
    {"firstName": "Owner", "companyName": "Air Conditioning Warehouse", "city": "Gosford", "state": "NSW", "email": "sales.centralcoast@acwa.biz"},
    {"firstName": "Owner", "companyName": "Broadwater Air and Energy", "city": "Gosford", "state": "NSW", "email": "info@broadwaterairandenergy.com.au"},
    {"firstName": "Owner", "companyName": "JH Commercial Services", "city": "Central Coast", "state": "NSW", "email": "enquiries@jhcommercial.com.au"},
    {"firstName": "Owner", "companyName": "Bear Air Conditioning", "city": "Central Coast", "state": "NSW", "email": "sales@bearairconditioning.com.au"},
]


# ===================================================
# HELPERS
# ===================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def ghl_request(method, path, body=None, version="2021-07-28"):
    url = f"{GHL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "AustraliaBlast/1.0 TheCallTaker",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        log(f"GHL API Error {e.code}: {method} {path} — {error_body[:300]}")
        return None
    except URLError as e:
        log(f"GHL Network Error: {method} {path} — {e.reason}")
        return None
    except Exception as e:
        log(f"GHL Error: {method} {path} — {e}")
        return None


def ntfy(topic, title, msg, priority="default", tags=""):
    try:
        url = f"https://ntfy.sh/{topic}"
        headers = {"Title": title, "Priority": priority, "Content-Type": "text/plain"}
        if tags:
            headers["Tags"] = tags
        req = Request(url, data=msg.encode(), headers=headers, method="POST")
        urlopen(req, timeout=10)
    except Exception as e:
        log(f"ntfy error: {e}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"sent": [], "failed": [], "created": [], "total_sent": 0, "started": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


# ===================================================
# EMAIL TEMPLATE — Pain Email (Email 1) — Australia Version
# ===================================================

def build_email_html(first_name, company_name, city, state):
    # Summer runs Dec-Feb in Australia, so Feb = peak AC season
    if state in ("QLD", "NT"):
        heat_line = f"In {city}, with summer temps hitting 40°C+, those emergency AC calls don't wait."
        seasonal = "Summer's still going strong — every missed call is a lost repair job."
    elif state in ("VIC", "TAS", "ACT"):
        heat_line = f"When {city} hits a 38°C day, customers don't wait — they call whoever picks up first."
        seasonal = "This summer's heatwaves have homeowners scrambling — every missed call is a lost job."
    elif state == "WA":
        heat_line = f"In {city}, with Perth summers regularly cracking 40°C, those emergency calls don't wait."
        seasonal = "Summer isn't slowing down — every missed call is real money walking out the door."
    elif state == "SA":
        heat_line = f"Adelaide summers routinely hit 40°C+. When the AC dies, customers call whoever picks up."
        seasonal = "Peak summer demand is still here — every missed call is a job your competitor takes."
    else:
        heat_line = f"In {city}, when a heatwave hits, customers don't wait — they call whoever picks up first."
        seasonal = "Summer's still cooking — every missed call is a lost service job."

    return f"""<div style="font-family: Arial, sans-serif; max-width: 600px; color: #222;">
<p>Hey {first_name},</p>

<p>I called {company_name} after hours recently. Got your voicemail.</p>

<p>No offence — I'm not a customer. But here's the thing: real customers are doing the exact same thing right now. Their AC goes out in the heat, they Google "air conditioning near me," and they start calling. First company that picks up gets the job.</p>

<p>If that's not you, it's your competitor down the road.</p>

<p>Here's what most AC business owners don't realise: <strong>85% of callers won't leave a voicemail.</strong> They just hang up and call the next bloke. The average AC service call is around $350-$500. So every missed call isn't just an inconvenience — it's real money walking out the door.</p>

<p>Think about it. If you're missing just 3 calls a week after hours, that's potentially <strong>$4,500-$6,000/month in lost revenue</strong>. Every month. All year. {heat_line}</p>

<p>{seasonal}</p>

<p>I built something that fixes this. It's called <strong>The Call Taker</strong> — an AI receptionist that answers every call to your business 24/7. No voicemail. No missed jobs. It talks to your customers like a real person, gets their info, and books the appointment right on your calendar.</p>

<p>Would you be open to a quick demo? Takes 15 minutes and you'll actually call the AI yourself so you can hear how it sounds.</p>

<p>Just reply "show me" and I'll send over some times. Or check it out here: <a href="https://thecalltaker.com/book.html">thecalltaker.com/book</a></p>

<p>— Wallace</p>

<p><em>P.S. I came from the trades. I've seen this problem kill good businesses. That's why I built this.</em></p>
</div>"""


# ===================================================
# MAIN BLAST
# ===================================================

def create_contact(lead):
    """Create contact in GHL. Returns contact_id or None."""
    body = {
        "firstName": lead.get("firstName", "Owner"),
        "companyName": lead["companyName"],
        "email": lead.get("email", ""),
        "locationId": GHL_LOCATION_ID,
        "tags": ["cold-outreach", "australia", "overnight-blast"],
        "source": "Australia Blast Feb 2026",
        "city": lead.get("city", ""),
        "state": lead.get("state", ""),
        "country": "Australia",
    }
    resp = ghl_request("POST", "/contacts/", body)
    if resp and "contact" in resp:
        return resp["contact"]["id"]
    if resp and "id" in resp:
        return resp["id"]
    return None


def send_email(contact_id, subject, html_body):
    """Send email via GHL conversations API."""
    body = {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body,
        "emailFrom": FROM_EMAIL,
    }
    resp = ghl_request("POST", "/conversations/messages", body, version="2021-04-15")
    if resp:
        return True
    return False


def run_blast():
    state = load_state()
    state["started"] = datetime.now().isoformat()
    already_sent = set(state.get("sent", []))
    sent_count = 0
    fail_count = 0

    ntfy(NTFY_OPS_TOPIC,
         "AUSTRALIA BLAST STARTING",
         f"Sending cold emails to {len(AUSTRALIA_LEADS)} Australian AC companies.\nStarting at {datetime.now().strftime('%I:%M %p')}.",
         priority="high", tags="rocket,australia")

    log(f"=== AUSTRALIA BLAST: {len(AUSTRALIA_LEADS)} leads ===")

    for i, lead in enumerate(AUSTRALIA_LEADS):
        company = lead["companyName"]

        if company in already_sent:
            log(f"Skipping {company} — already sent")
            continue

        if not lead.get("email"):
            log(f"Skipping {company} — no email")
            state["failed"].append(company)
            save_state(state)
            continue

        log(f"[{i+1}/{len(AUSTRALIA_LEADS)}] Processing {company} ({lead.get('city', 'AU')}, {lead.get('state', '')})...")

        # Create contact
        contact_id = create_contact(lead)
        if not contact_id:
            log(f"FAILED to create contact for {company}")
            state["failed"].append(company)
            fail_count += 1
            save_state(state)
            time.sleep(3)
            continue

        state["created"].append(company)
        log(f"Created contact: {company} -> {contact_id}")

        # Send email
        first = lead.get("firstName", "there")
        subject = f"I called {company} after hours recently"
        html = build_email_html(first, company, lead.get("city", ""), lead.get("state", ""))

        if send_email(contact_id, subject, html):
            sent_count += 1
            state["sent"].append(company)
            state["total_sent"] = state.get("total_sent", 0) + 1
            log(f"EMAIL SENT to {company} ({lead.get('email')})")
        else:
            log(f"FAILED to send email to {company}")
            state["failed"].append(company)
            fail_count += 1

        save_state(state)

        # Rate limit
        if i < len(AUSTRALIA_LEADS) - 1:
            time.sleep(DELAY_BETWEEN_EMAILS)

        # Progress update every 25
        if (i + 1) % 25 == 0:
            ntfy(NTFY_OPS_TOPIC,
                 f"Australia Blast Progress: {i+1}/{len(AUSTRALIA_LEADS)}",
                 f"Sent: {sent_count} | Failed: {fail_count} | Remaining: {len(AUSTRALIA_LEADS) - i - 1}",
                 tags="chart_with_upwards_trend")

    # Final report
    summary = (
        f"AUSTRALIA BLAST COMPLETE\n"
        f"{'='*30}\n"
        f"Total leads: {len(AUSTRALIA_LEADS)}\n"
        f"Contacts created: {len(state.get('created', []))}\n"
        f"Emails sent: {sent_count}\n"
        f"Failed: {fail_count}\n"
        f"Finished: {datetime.now().strftime('%I:%M %p')}\n"
        f"\nAll leads tagged: cold-outreach, australia, overnight-blast\n"
        f"Max will auto-follow-up on replies.\n"
        f"\nCoverage: NSW, VIC, QLD, WA, SA, TAS, NT, ACT"
    )

    ntfy(NTFY_WAR_TOPIC,
         f"AUSTRALIA BLAST DONE — {sent_count} emails sent",
         summary,
         priority="high", tags="tada,email,australia")

    log(summary)
    save_state(state)


if __name__ == "__main__":
    run_blast()
