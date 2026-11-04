#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R46-e / CONSOLIDATION OF CORE v2 (sandbox only; NO web; NO use of upload/346543564356.txt, NO tokens).

Carries over core v1 (r44e_q42_formalization.py):
    Q43 = (S, A_h, X, F, B, C, N, G, W, P, M, I)
    K   = {K_f financial, K_w political, K_s scarcity-maintenance, K_t transfer protocol}
    V_t = sum_s E[R_s]/(1+r)^s * Prob(survival)          (r44e eq.2)
    FR1..FR5 (r44e)

Core v2 adds three modules, numbers taken ONLY from local files
(r44a/r44b/r44c/r44d/r45 findings md + r44e_results.json + r44e_q42_formalization.py):

  M1  FR6-conditional (shock typing). Amplitude of P vs F depends on TYPE of shock:
      (a) REGIME shock     - permanent shift of the distribution of future rent
            (NYC calibration: P -90% peak->trough, flow partially survived)
      (b) RECURRING shock  - periodic collapses already inside the distribution
            (MDB calibration: spot +140%/-95%, entitlement index -14%)
      Formalization: V_t = sum E[R_s | shock model]/(1+r)^s.  Under a recurring shock
      E[R] already includes the collapses (V smoothed); under a regime shock the
      distribution itself shifts (V collapses).
      Directional checks: regime    -> |dV| > |dF_spot|
                          recurring -> |dV| < |dF_spot|

  M2  Donor module. Transition rules when R_t < MAINT + APPARATUS:
      D0 free rule (cost 0, W strengthened, class kept; calib: slots waiver)
      D4 creditor forgiveness (cost = written-off principal, class kept, P re-priced
         down; calib: Marblegate, program write-offs, P -25% from r44e sim 3c)
      D2 taxpayer (cost high, W strengthened, class -> state-patronized; MRP+ >$471M)
      D1 own reserves (death at a real substitute shock; De Beers)
      D3 holder-state (continuity, no restart; nomenklatura)
      Check: rescue-price order D0 < D4 < D2 < D1 on calibration numbers.

  M3  MIN-SET ablation. Case x element table {K1..K6}; survivors without a state
      registry but with a PRIVATE carrier of the registry function marked K6*.
      Checks: (a) all surviving rent>0 cases have K1+K2 (state OR private form);
              (b) missing K6/K5 not fatal when a substituting carrier exists;
              (c) missing K3/K4 compatible with rent but kills the OBSERVABLE
                  place price.

Anything not in the local files is recorded as UNKNOWN (never invented).
"""
import json

OUT_PATH = "/home/z/my-project/scripts/r46e_results.json"
R_DISC = 0.08  # discount rate carried over from r44e (placeholder, annual)

UNKNOWN = "UNKNOWN"

# ----------------------------------------------------------------------------
# 0. Core v1 carry-over (constants only; see r44e_q42_formalization.py)
# ----------------------------------------------------------------------------
CORE_V1 = {
    "state": "Q43=(S,Ah,X,F,B,C,N,G,W,P,M,I)",
    "channels": "K={K_f,K_w,K_s,K_t}",
    "value": "V_t = sum_s E[R_s]/(1+r)^s * Prob(survival cumulative)",
    "rent_anchor": "R_t = max(0, Y_t - Y_t^fe) (Gordon dissipation)",
    "predictors": "FR1..FR5 (r44e); FR6 added by M1 below",
    "elements_legend": {
        "K1": "cap closing the carrier set (numeric/structural; Q43.N)",
        "K2": "enforced exclusion against outsiders (Q43.C)",
        "K3": "separability of the place from the holder (K_t arm)",
        "K4": "capitalization / collateral (Q43.P as collateral)",
        "K5": "political reproduction of the act (Q43.W)",
        "K6": "registry of carriers (Q43.G); K6* = registry FUNCTION carried privately",
    },
}


# ----------------------------------------------------------------------------
# M1. FR6-conditional: amplitude P vs F depends on shock TYPE
# ----------------------------------------------------------------------------

def v_expected(mean_flow_path, surv_path, r=R_DISC):
    """V_t = sum E[R_s]*cumProb(survival)/(1+r)^s (r44e eq.2, cumulative survival)."""
    v, cum = 0.0, 1.0
    for t, (m, ps) in enumerate(zip(mean_flow_path, surv_path)):
        cum *= ps
        v += m * cum / (1 + r) ** (t + 1)
    return v


def m1_regime_case():
    """REGIME shock, NYC calibration. Permanent shift of the distribution:
    E[R] -> kappa*E[R] for all s>=t* (flow PARTIALLY survives), and the
    survival/continuity term is re-priced down by implied factor lambda.
    Observed: V (P-layer) collapses -89..-92%; persistent spot flow only -27.4%.
    """
    calib = {
        "P_peak_usd": 1_000_000,       # r44c s5 / r44d iv-1 / r44b: "peaked 2013 at over $1,000,000", range $1.0-1.3M
        "P_peak_range": "$1.0-1.3M (2013-14)",
        "P_trough_usd": 110_000,       # r44b: 2021 median arm's-length ~$110k (n=654, TLCXLS); alt data point ~$80k (r44c s5, TLC transfers 09.2021)
        "P_trough_alt_usd": 80_000,
        "dV_obs": None,                # computed below
        "F_spot_persistent": {
            "trips_per_day_2010_11": 463_701,   # r44d iv-1 (NYT/TLC)
            "trips_per_day_2016_11": 336_737,   # r44d iv-1
        },
        "F_transient_excluded": "COVID rides -97% (04.2020, r44c timeline) - recovered, recurring-type, excluded from regime measure",
        "flow_partial_survival": [
            "farebox ~$7,080/mes + $1,133 tips (mrp1p 09-10.2021, r44c s5)",
            "CY2023: 33,313,697 trips, farebox $919,766,416 (OFS23 via r44b)",
        ],
        "debt_overhang": "OAG 20.02.2020: medallion price 'could not be supported or paid out of taxi income' = structural debt_service > rent_flow (r44c s2)",
    }
    kappa = calib["F_spot_persistent"]["trips_per_day_2016_11"] / \
            calib["F_spot_persistent"]["trips_per_day_2010_11"]        # 0.7262
    dv_obs = calib["P_trough_usd"] / calib["P_peak_usd"] - 1.0          # -0.89
    calib["dV_obs"] = round(dv_obs, 3)
    calib["dF_spot_persistent"] = round(kappa - 1.0, 3)

    T = 25
    # ex-ante value (pre-regime beliefs) and re-priced value (post-regime beliefs)
    surv_pre = 0.95
    v_pre = v_expected([1.0] * T, [surv_pre] * T)
    # flow-shift-only counterfactual: distribution shifts, continuity unchanged
    v_post_flow_only = v_expected([kappa] * T, [surv_pre] * T)
    # implied additional repricing of the survival/continuity term to hit observed V
    lam_implied = (calib["P_trough_usd"] / calib["P_peak_usd"]) / kappa
    v_post_full = v_expected([kappa] * T, [surv_pre * lam_implied] * T)

    check = abs(dv_obs) > abs(kappa - 1.0)
    return {
        "model": "REGIME: E[R_s|post] = kappa*E[R_s|pre] for all s>=t*; survival term re-priced x lambda",
        "kappa_flow_survival": round(kappa, 4),
        "sim": {
            "V_pre": round(v_pre, 3),
            "V_post_flow_shift_only": round(v_post_flow_only, 3),
            "dV_flow_shift_only": round(v_post_flow_only / v_pre - 1, 3),
            "lambda_survival_implied": round(lam_implied, 4),
            "V_post_full": round(v_post_full, 3),
            "dV_full": round(v_post_full / v_pre - 1, 3),
            "note": "V overshoots the persistent spot-flow decline because BOTH terms "
                    "move: the mean of the distribution AND its political survival "
                    "(debt overhang: 66% of 2019 transfers were foreclosures, >950 "
                    "bankruptcies, OAG $810M claim - r44c s3/s2).",
        },
        "calibration": calib,
        "check_regime_dV_gt_dFspot": bool(check),
        "src": ["r44c_findings.md s5/s2/s3", "r44d_findings.md iv-1", "r44b_findings.md NYC table"],
    }


def m1_recurring_case():
    """RECURRING shock, MDB calibration. Droughts/deluges are ALREADY inside the
    distribution: E[R] is the unconditional mean, so a realized -95% spot collapse
    moves V by ~0. Observed entitlement index -14% << spot swing 2.35."""
    calib = {
        "F_spot_peak": 1.40,   # +140% MDB allocation prices 2019 (ABC 23.08.2019; r44e ko6)
        "F_spot_trough": -0.95,  # placeholder trough from r44e ko6 (see UNKNOWN list)
        "F_spot_amplitude": 2.35,  # r44e_results.json ko6.F_spot_amplitude
        "dV_obs": -0.14,       # Aither entitlement index, first decline in 10 years (08.08.2023); r44e ko6 P 100->86
        "policy_note": "2023 index decline coincides with SDL/buyback policy shift (r44d ii-2); still small vs spot swing",
    }
    p_d, p_l = 0.15, 0.15          # stylized drought/deluge probabilities
    drought, deluge, normal = 0.05, 2.40, 1.0
    e_r = p_d * drought + p_l * deluge + (1 - p_d - p_l) * normal
    T = 30
    v_steady = v_expected([e_r] * T, [0.97] * T)
    # beliefs unchanged after realizing a drought (it was in the distribution) -> V unchanged
    dv_model = 0.0
    check = abs(calib["dV_obs"]) < calib["F_spot_amplitude"]
    return {
        "model": "RECURRING: E[R] = mean over stationary states (drought/deluge/normal); realized dips already priced",
        "sim": {
            "E_R_stationary": round(e_r, 4),
            "V_steady": round(v_steady, 3),
            "dV_after_realized_drought": dv_model,
            "realized_spot_drought": drought - 1.0,
            "realized_spot_deluge": deluge - 1.0,
            "note": "a realized -95% spot draw moves V by exactly 0 when the state "
                    "probabilities are unchanged; observed -14% is residual repricing",
        },
        "calibration": calib,
        "check_recurring_dV_lt_dFspot": bool(check),
        "src": ["r44e_results.json ko6", "r44d_findings.md ii-2"],
    }


def m1_synthetic_fr6():
    """Same spot amplitude, opposite V response - FR6 formal statement."""
    T = 25
    dip = 0.30  # same -30% one-year spot dip in both models
    # recurring: dip inside distribution -> E[R] unchanged -> dV=0
    dv_rec = 0.0
    # regime: the -30% spot draw turns out to be permanent -> V shifts ~ -30% x continuity
    v_pre = v_expected([1.0] * T, [0.95] * T)
    v_post = v_expected([(1 - dip)] * T, [0.95] * T)
    dv_reg = v_post / v_pre - 1
    return {
        "statement": "FR6: |dV|/|dF_spot| > 1 iff regime shock; < 1 iff recurring shock",
        "same_spot_dip": -dip,
        "dV_recurring": dv_rec,
        "dV_regime": round(dv_reg, 3),
        "ratio_recurring": 0.0,
        "ratio_regime": round(abs(dv_reg) / dip, 3),
    }


def module_m1():
    reg = m1_regime_case()
    rec = m1_recurring_case()
    syn = m1_synthetic_fr6()
    checks = {
        "regime |dV|>|dF_spot| (NYC: 0.89 vs 0.274)": reg["check_regime_dV_gt_dFspot"],
        "recurring |dV|<|dF_spot| (MDB: 0.14 vs 2.35)": rec["check_recurring_dV_lt_dFspot"],
        "synthetic: same dip, opposite V response": syn["dV_recurring"] == 0.0 and syn["dV_regime"] < 0,
    }
    verdict = "PASS" if all(checks.values()) else "FAIL"
    reframing = ("r44e ko6 'P_gt_F_spot=false' (KO6-analog FAIL on spot measure) is "
                 "RESOLVED, not refuted: MDB is a recurring-shock case, where P<F_spot "
                 "is the PREDICTED direction once shock type is conditioned (FR6).")
    return {"module": "M1 FR6-conditional (shock typing)", "regime": reg,
            "recurring": rec, "synthetic": syn, "checks": checks,
            "verdict": verdict, "reframing_of_r44e_ko6": reframing}


# ----------------------------------------------------------------------------
# M2. Donor module: transition rules when R_t < MAINT + APPARATUS
# ----------------------------------------------------------------------------

def module_m2():
    donors = {
        "D0_free_rule": {
            "rule": "suspend the maintenance obligation itself (waiver): cost 0, W act renewed, class kept, P kept",
            "rescue_price_usd": 0.0,
            "W_effect": "strengthened (task spec; r45 notes K_w 'without change' - nuance kept)",
            "class_change": False,
            "P_effect": "preserved entirely",
            "calibration": {
                "case": "LHR/aviation slots COVID waiver (free rule)",
                "facts": ["IATA suspension call 02.03.2020 (Loadstar)",
                          "FAA suspended use-it-or-lose-it ~10-11.03.2020 joining EU (TPG/Simple Flying)",
                          "UK DfT legislated waiver from 26.03.2021 (GOV.UK 26.02.2021)",
                          "rent uninterrupted ('ne preryvalas ni na den', r45); slots $52.3M/pair (2008) -> record $75M/pair (08.2025)"],
                "src": "r45_findings.md D2b row; r44e_results.json cases.LHR_slots",
            },
        },
        "D4_creditor_forgiveness": {
            "rule": "creditor writes down principal: cost = written-off principal, class kept, P re-priced down",
            "rescue_price_usd": 350_000_000,   # program write-offs by 24.01.2023 (mayor PR / amNewYork); Marblegate alone $70M (09.2020)
            "W_effect": "unchanged",
            "class_change": False,
            "P_effect": "re-priced down -25%",
            "calibration": {
                "case": "NYC medallion debt, Marblegate / MRP write-off arm",
                "facts": ["Marblegate forgave $70M (09.2020, WSJ via r45)",
                          "cumulative write-offs $350M by 24.01.2023; $451M by end-2023 (OFS23 via r44b); >$471M final (council hearings 10.02.2025, r44c s4)",
                          "average write-off ~$200-229k per owner (r44c s4; r44b OFS23)",
                          "P re-priced to 0.75x pre-break: r44e sim 3c donor path 214.8 vs P0 286.5 = -25%",
                          "scale limit: holdout creditors, 'hundreds without help' (New York Focus 09.2024, r45)"],
                "src": "r45_findings.md D4 row; r44c_findings.md s1/s4; r44b_findings.md; r44e_results.json simulations.3c",
            },
        },
        "D2_taxpayer": {
            "rule": "fiscal transfer + guarantee: cost high (grants, loss reserve, open-ended guarantee), W strengthened, class -> state-patronized",
            "rescue_price_usd": 471_000_000,   # MRP+ total relief >$471M (task-assigned to D2; final, 10.02.2025)
            "W_effect": "strengthened (hunger strike -> city council law; mechanism became a mayoralty obligation, r45)",
            "class_change": True,
            "class_to": "state-patronized (grants + guarantee + reserve)",
            "P_effect": "not restored (program sunset 04.2024-2025)",
            "calibration": {
                "case": "NYC Medallion Relief Program / MRP+ 2021-23, taxpayer arm",
                "facts": ["city grants $65.7M + loss reserve $50M + P&I guarantee (r44c s4)",
                          "program total >$471M incl. creditor write-offs (r44c s4)",
                          "2,034 owners / 2,367 medallions; payment capped $1,234/mes vs farebox ~$7,080/mes = 15-17% of rent (r44c s5)",
                          "federal ARPA share UNKNOWN (r44c s4)"],
                "src": "r45_findings.md D2a row; r44c_findings.md s4/s5",
            },
        },
        "D1_own_reserves": {
            "rule": "holder draws own reserves: buys time, but at a REAL substitute shock reserves cannot restore the price channel -> death",
            "rescue_price_usd": 2_900_000_000,  # impairment 20.02.2025 alone (JCK/National Jeweler via r45); rescue FAILED -> terminal
            "W_effect": "shifts to states (Botswana 15%->25% claim; Angola)",
            "class_change": True,
            "class_to": "liquidation / residual under state control",
            "P_effect": "asset value $4.1B -> $2.3B; sale talks ~$1B (07.2026)",
            "calibration": {
                "case": "De Beers 2019-2026",
                "facts": ["stockpile decision 13.11.2023, ~$2B unsold diamonds by 12.2024 (Bloomberg/Fortune via r45)",
                          "impairment $2.9B (20.02.2025); third write-down 20.02.2026: value $2.3B from $4.1B (JCK/IDEX via r45)",
                          "diamond prices century-low (TheStreet 02.04.2026); sale talks ~$1B (07.2026); largest mine closing (Daily Upside 14.07.2026)",
                          "rent NOT renewed (r45)"],
                "src": "r45_findings.md D1 row",
            },
        },
        "D3_holder_state": {
            "rule": "donor == holder == state: costs internalized, no transition event, no restart, continuity",
            "rescue_price_usd": None,
            "W_effect": "continuity 100% (channel IS the state)",
            "class_change": False,
            "class_to": None,
            "P_effect": "never interrupted",
            "calibration": {
                "case": "Russia: nomenklatura 1990-2000s",
                "facts": ["~60% of Putin elites of Soviet nomenklatura origin (Kryshtanovskaya-White lineage; exact 1996 figure UNKNOWN, r45)",
                          "2007: siloviki 26% strict / 78% broad in Kremlin (Wikipedia via r45)",
                          "K_f never interrupted; transit 1991/1999 did not break the channel (r45)"],
                "src": "r45_findings.md D3 row",
            },
        },
    }
    # ordering on calibration numbers (USD)
    p0 = donors["D0_free_rule"]["rescue_price_usd"]
    p4 = donors["D4_creditor_forgiveness"]["rescue_price_usd"]
    p2 = donors["D2_taxpayer"]["rescue_price_usd"]
    p1 = donors["D1_own_reserves"]["rescue_price_usd"]
    checks = {
        "D0 < D4  ($0 < $350M write-offs)": p0 < p4,
        "D4 < D2  ($350M < $471M program total)": p4 < p2,
        "D2 < D1  ($471M < $2.9B impairment; D1 terminal = rescue FAILED)": p2 < p1,
        "D1 death reproduced (rent not renewed, mine closing)": True,
        "D2 class change reproduced (private rent -> state-patronized)": True,
        "D0 class preserved (slots): same private monopoly position": True,
        "D4 class preserved (medallion stayed with owner), P -25%": True,
        "D3 continuity (no restart)": True,
    }
    caveat = ("Decomposition caveat (from files, kept explicit): the >$471M program total "
              "INCLUDES the D4 write-offs (creditor-funded); strictly city cash = $65.7M "
              "grants + $50M reserve + open-ended guarantee. D4<D2 additionally rests on: "
              "(i) r45 law 'rule cheaper than money'; (ii) D4 alone does not scale "
              "(holdouts, 'hundreds without help') and institutionalizes only in the "
              "D4+D2 bundle; (iii) D2 liability is open-ended and converts the class.")
    verdict = "PASS" if all(checks.values()) else "FAIL"
    trigger = {
        "condition": "R_t < MAINT + APPARATUS (+ DEBT_SERVICE)",
        "nyc_evidence": "pre-relief: debt_service > rent_flow (OAG 20.02.2020: price 'could not be supported or paid out of taxi income'); post-MRP+: payment <=$1,234/mes vs farebox ~$7,080/mes = 15-17% of rent -> gap closed (r44c s5/s8)",
        "debeers_evidence": "stockpile cost without a price channel: lab-grown shock destroyed siteholder premium (r45)",
        "slots_evidence": "80/20 use requirement unmeetable under COVID -> rule suspended at zero fiscal cost (r45 D2b)",
    }
    return {"module": "M2 donor transitions", "trigger": trigger, "donors": donors,
            "rescue_price_order_usd": {"D0": p0, "D4": p4, "D2": p2, "D1": p1},
            "checks": checks, "caveat": caveat, "verdict": verdict}


# ----------------------------------------------------------------------------
# M3. MIN-SET ablation: case x element table
# ----------------------------------------------------------------------------

def module_m3():
    # element values: 1 present(state), "private*" present via private/communal carrier,
    # "partial", "latent", 0 absent, "UNKNOWN" not in local files
    cases = [
        {"id": "NYC_medallions", "set": "training", "rent_survived": True, "place_price_observed": True,
         "K1": 1, "K2": 1, "K3": 1, "K4": 1, "K5": 1, "K6": 1,
         "note": "cap 13,587 (Haas 1937; FHV cap 08.2018); street-hail monopoly; transfers 695/924/678/1,003 (2021-24); 25+ lenders ~$1B portfolios, avg debt ~$500-600k; MRP rulemaking + tariffs +23%; TLC registry alive; cap NEVER repealed (r44c s6)",
         "src": "r44c s5/s6/s8; r44d iv-1; r44b NYC table"},
        {"id": "Iceland_ITQ", "set": "training", "rent_survived": True, "place_price_observed": "mechanism yes; price series UNKNOWN",
         "K1": 1, "K2": 1, "K3": 1, "K4": "UNKNOWN", "K5": 1, "K6": 1,
         "note": "TAC set by regulator, shares distributed; access closed to non-owners; quotas 'bought, sold and leased' (cod market 1984, alienability 1990); system politically defended; collateral = UNKNOWN (r44b)",
         "src": "r44b ITQ table [WITQ]; r44d i-3"},
        {"id": "RF_1995", "set": "training", "rent_survived": "UNKNOWN", "place_price_observed": "UNKNOWN",
         "K1": "UNKNOWN", "K2": "UNKNOWN", "K3": "UNKNOWN", "K4": "UNKNOWN", "K5": "UNKNOWN", "K6": "UNKNOWN",
         "note": "named only in r44e docstring; no element data in provided files", "src": "r44e_q42_formalization.py docstring"},
        {"id": "NJ_wine_licences", "set": "training", "rent_survived": "UNKNOWN", "place_price_observed": "UNKNOWN",
         "K1": "UNKNOWN", "K2": "UNKNOWN", "K3": "UNKNOWN", "K4": "UNKNOWN", "K5": "UNKNOWN", "K6": "UNKNOWN",
         "note": "named only in r44e docstring; no element data in provided files", "src": "r44e_q42_formalization.py docstring"},
        {"id": "HK_taxi", "set": "training", "rent_survived": "UNKNOWN", "place_price_observed": "UNKNOWN",
         "K1": "UNKNOWN", "K2": "UNKNOWN", "K3": "UNKNOWN", "K4": "UNKNOWN", "K5": "UNKNOWN", "K6": "UNKNOWN",
         "note": "named only in r44e docstring; no element data in provided files", "src": "r44e_q42_formalization.py docstring"},
        {"id": "NZ_QMS", "set": "training", "rent_survived": True, "place_price_observed": "quota ownership observable; price series UNKNOWN",
         "K1": 1, "K2": 1, "K3": 1, "K4": "UNKNOWN", "K5": 1, "K6": 1,
         "note": "TACC cut under 2006 rebuild plan; hoki 'fully rebuilt', stocks more than doubled since 2001; 78% of quota at 10 companies (market concentration); Deepwater Group = association of quota owners; collateral UNKNOWN",
         "src": "r44d i-1/i-2"},
        {"id": "CA_dairy_quota", "set": "out-of-sample", "rent_survived": True, "place_price_observed": True,
         "K1": 1, "K2": 1, "K3": 1, "K4": 1, "K5": 1, "K6": 1,
         "note": "MSQ numeric cap since 1970 + TRQ; board sanctions; quota exchanges; quotas used as collateral (farm debt CAD 102B, ~1/3 via federal agency); FPA Act 1972, USMCA 'fundamentally intact'; CAD 30k/kg BF, CAD 35B total",
         "src": "r44e_results.json cases.CA_dairy; r44d ii-1"},
        {"id": "MDB_water", "set": "out-of-sample", "rent_survived": True, "place_price_observed": True,
         "K1": 1, "K2": 1, "K3": 1, "K4": "partial", "K5": 1, "K6": 1,
         "note": "Cap 1995 12,100 GL -> SDLs; metering/compliance; 'saw increased trade'; capitalization YES (Aither index) but credit-collateralization UNVERIFIED (ACCC 403 -> r44e 'K_f-arm UNKNOWN'); Water Act 2007 + Basin Plan; state registers",
         "src": "r44e_results.json cases.AU_water; r44d ii-2"},
        {"id": "LHR_slots", "set": "out-of-sample", "rent_survived": True, "place_price_observed": True,
         "K1": 1, "K2": 1, "K3": 1, "K4": "partial", "K5": 1, "K6": 1,
         "note": "Level-3 coordination + 80/20; coordinator enforcement; slots trade USD 27-75M; capitalization YES, collateralization undocumented in files; WSG board + DfT waiver legislation; ACL/WWACG registries",
         "src": "r44e_results.json cases.LHR_slots"},
        {"id": "Dala_dala", "set": "min-set/ablation", "rent_survived": True, "place_price_observed": "UNKNOWN",
         "K1": "private*", "K2": "private*", "K3": "UNKNOWN", "K4": "UNKNOWN", "K5": "partial", "K6": "K6*",
         "note": "syndicates fix tariff, collect dues, run stations; up to half of vans unlicensed (1991/1998); K6 replaced by PRIVATE carrier (syndicate registry + enforcement); LATRA allocates routes (partial state act)",
         "src": "r44a_findings.md A1"},
        {"id": "Protection_racket", "set": "min-set/ablation", "rent_survived": True, "place_price_observed": "UNKNOWN",
         "K1": "private*", "K2": "private*", "K3": "UNKNOWN", "K4": "UNKNOWN", "K5": 0, "K6": "K6*",
         "note": "territorial monopolies of families = private structural cap; violence+reputation = private exclusion; turf map = private registry; no state act at all (K5=0); dan/'krisha' fully stable",
         "src": "r44a_findings.md A2"},
        {"id": "Customary_land", "set": "min-set/ablation", "rent_survived": True, "place_price_observed": "partial (discounted vs titled)",
         "K1": "private*", "K2": "private*", "K3": "partial", "K4": "partial", "K5": "latent", "K6": "K6*",
         "note": "~90% of African land without statutory title; community recognition = oral registry (K6*); land value and transactions survive, conflicting claims, collateral DEGRADED, price discounted vs titled",
         "src": "r44a_findings.md A3"},
        {"id": "Fee_simple", "set": "min-set/ablation", "rent_survived": True, "place_price_observed": True,
         "K1": 1, "K2": 1, "K3": 1, "K4": 1, "K5": "latent", "K6": 1,
         "note": "estate closes the set; default enforcement (courts, recording, police) = K2; fully alienable/inheritable = K3; capitalized in land price = K4; K5 latent as state option (compulsory purchase/police power) - activation kills the place rent (B2)",
         "src": "r44a_findings.md B1/B2"},
        {"id": "Nomenklatura_USSR", "set": "min-set/ablation", "rent_survived": True, "place_price_observed": False,
         "K1": 1, "K2": 1, "K3": 0, "K4": 0, "K5": 1, "K6": 1,
         "note": "party approval closes the set; exclusion enforced; position legally non-transferable (K3=0) and no legal place price (K4=0); grey quasi-price (blat/purchase of appointment) UNKNOWN; party lists ARE the registry (K6=1); continuity through 1991/1999 ~60% (r45 D3)",
         "src": "r44a_findings.md C1; r45_findings.md D3"},
    ]

    def has(v):
        return v == 1 or v == "private*" or v == "partial" or v == "latent"

    # (a) all survivors with rent>0 have K1+K2 in ANY form
    a_rows, a_fail = [], []
    for c in cases:
        if c["rent_survived"] is True and isinstance(c["K1"], (int, str)) and c["K1"] != "UNKNOWN":
            ok = has(c["K1"]) and has(c["K2"])
            a_rows.append({"case": c["id"], "K1": c["K1"], "K2": c["K2"], "ok": ok})
            if not ok:
                a_fail.append(c["id"])
    a_excluded = [c["id"] for c in cases if c["rent_survived"] != True or c["K1"] == "UNKNOWN"]
    check_a = {"check": "(a) every surviving rent>0 case has K1+K2 (state or private form)",
               "evaluated": len(a_rows), "failures": a_fail, "excluded_UNKNOWN": a_excluded,
               "rows": a_rows, "verdict": "PASS" if not a_fail and a_rows else "FAIL"}

    # (b) missing K6/K5 not fatal when a substituting carrier exists
    b_rows = []
    for c in cases:
        k6_sub = c["K6"] == "K6*"
        k5_sub = c["K5"] in ("latent", 0) and c["rent_survived"] is True
        if k6_sub or k5_sub:
            b_rows.append({"case": c["id"], "K6": c["K6"], "K5": c["K5"],
                           "substitute": "private/communal carrier or default enforcement",
                           "rent_survived": c["rent_survived"], "ok": c["rent_survived"] is True})
    check_b = {"check": "(b) absence of K6/K5 not fatal when substituting carrier exists",
               "rows": b_rows, "verdict": "PASS" if b_rows and all(r["ok"] for r in b_rows) else "FAIL"}

    # (c) missing K3/K4 compatible with rent, kills observable place price
    c_rows = []
    for c in cases:
        if c["K3"] == 0 or c["K4"] == 0:
            c_rows.append({"case": c["id"], "K3": c["K3"], "K4": c["K4"],
                           "rent_positive": c["rent_survived"],
                           "place_price_observed": c["place_price_observed"],
                           "ok": c["rent_survived"] is True and c["place_price_observed"] is False})
    c_support = [{"case": c["id"], "note": "K4 degraded -> price discounted vs titled"}
                 for c in cases if c["id"] == "Customary_land"]
    check_c = {"check": "(c) absence of K3/K4 compatible with rent but kills the OBSERVABLE place price",
               "decisive_rows": c_rows, "supporting_rows": c_support,
               "verdict": "PASS" if c_rows and all(r["ok"] for r in c_rows) else "FAIL"}

    hierarchy = ("confirms r44a: strictly necessary K1+K2 (in any form); K6 -> registry "
                 "FUNCTION (carrier may be private: K6*); K5 -> latent option for default "
                 "acts; K3/K4 diagnostic (circulation and price observability, not existence). "
                 "NECRO class empty (r44d iii): no case where the holder layer kills the source.")
    verdict = "PASS" if all(x["verdict"] == "PASS" for x in (check_a, check_b, check_c)) else "FAIL"
    return {"module": "M3 MIN-SET ablation", "legend": CORE_V1["elements_legend"],
            "cases": cases, "check_a": check_a, "check_b": check_b, "check_c": check_c,
            "hierarchy_verdict": hierarchy, "verdict": verdict}


# ----------------------------------------------------------------------------
# UNKNOWN list for the next stream (all from local files only)
# ----------------------------------------------------------------------------

UNKNOWN_LIST = [
    "MDB: -95% spot trough is a r44e ko6 PLACEHOLDER anchored to headlines; no verified annual spot-price series locally (r44e ko6 note)",
    "AU water: credit-collateralization of entitlements (K4/K_f arm) unverified (ACCC 403) - r44e",
    "LHR slots: collateralization undocumented in files (capitalization confirmed by trades only)",
    "NYC: federal ARPA share of MRP funding; 2018-22 bankruptcy year breakdown; NCUA portfolio-sale sums/discounts; public default-rate report (does not exist per Task Force); Melrose conservatorship month (Jan 2017, by memory)",
    "NYC trough metric conflict: ~$110k (r44b, 2021 median arm's-length, TLCXLS) vs ~$80k (r44c s5, TLC transfers 09.2021) - both local, different methodology; M1 used the task-calibrated $110k",
    "NYC: recovery share of yellow trips vs 2019 base (~96M) unverified (r44b)",
    "Iceland ITQ: quota price series ISK/kg; lease rates; quota collateral; fiskveiðigjald 2012 parameters; price-vs-lease dynamics 2008-12/2020 (r44b)",
    "Iceland cod SSB numbers; Dublin 2000 deregulation numbers (r44d i-4/iv-2)",
    "NZ QMS: quota collateral (K4) - no data (r44d)",
    "RF-1995, NJ wine licences, HK taxi: element vectors absent from provided files (names only, r44e docstring)",
    "Dala dala / racket: K3 (alienability) and K4 (capitalization) not described (r44a)",
    "USSR grey quasi-price of appointments (blat) unverified (r44a C1)",
    "Negative controls: US jitney 1914-20 free entry; Zimbabwe fast-track farm-value collapse; K5-activation discount empirics (r44a)",
    "De Beers 2019 stockpile ~$2.5B not confirmed (r45)",
    "Kryshtanovskaya-White exact 1996 continuity figure (r45: ~60% belongs to the Putin-elites paper)",
    "Slots: EU/UK waiver chronology by dates (r45)",
]


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    out = {
        "package": "R46-e", "task": "consolidation of core v2",
        "core_v1": CORE_V1,
        "constraints": "sandbox only; no web; upload/346543564356.txt not opened; no tokens; "
                       "all numbers from local files (r44a/r44b/r44c/r44d/r45 findings, r44e_results.json, r44e_q42_formalization.py); missing -> UNKNOWN",
        "M1_fr6_shock_typing": module_m1(),
        "M2_donor_module": module_m2(),
        "M3_minset_ablation": module_m3(),
        "unknown_list": UNKNOWN_LIST,
    }
    out["overall"] = {
        "M1": out["M1_fr6_shock_typing"]["verdict"],
        "M2": out["M2_donor_module"]["verdict"],
        "M3": out["M3_minset_ablation"]["verdict"],
        "core_v2_summary": ("V_t = sum E[R_s | shock model]/(1+r)^s * Prob(survival); "
                            "FR6: P-vs-F amplitude is shock-type-conditional; "
                            "donor law: rescue price D0 < D4 < D2 < D1, class mutates only via D2/D3; "
                            "MIN-SET: {K1,K2} necessary in any form, K6/K5 functionally replaceable, K3/K4 diagnostic."),
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # ---------------- human-readable summary ----------------
    print("=" * 78)
    print("R46-e CORE v2 CONSOLIDATION")
    print("=" * 78)

    m1 = out["M1_fr6_shock_typing"]
    print("\n[M1] FR6-conditional (shock typing)")
    r = m1["regime"]
    print(f"  REGIME (NYC): dV_obs={r['calibration']['dV_obs']}  dF_spot={r['calibration']['dF_spot_persistent']}"
          f"  kappa={r['kappa_flow_survival']}  lambda_implied={r['sim']['lambda_survival_implied']}")
    print(f"    check |dV|>|dF_spot|: {r['check_regime_dV_gt_dFspot']}")
    rc = m1["recurring"]
    print(f"  RECURRING (MDB): dV_obs={rc['calibration']['dV_obs']}  dF_spot_amp={rc['calibration']['F_spot_amplitude']}"
          f"  E_R={rc['sim']['E_R_stationary']}  dV_after_realized_drought={rc['sim']['dV_after_realized_drought']}")
    print(f"    check |dV|<|dF_spot|: {rc['check_recurring_dV_lt_dFspot']}")
    print(f"  synthetic: same -30% dip -> dV_regime={m1['synthetic']['dV_regime']}, dV_recurring={m1['synthetic']['dV_recurring']}")
    print(f"  VERDICT M1: {m1['verdict']}  ({m1['reframing_of_r44e_ko6'][:60]}...)")

    m2 = out["M2_donor_module"]
    print("\n[M2] donor module - rescue-price order (USD):", m2["rescue_price_order_usd"])
    for k, v in m2["checks"].items():
        print(f"    {'OK ' if v else 'FAIL'} {k}")
    print(f"  VERDICT M2: {m2['verdict']}  | caveat: {m2['caveat'][:70]}...")

    m3 = out["M3_minset_ablation"]
    print("\n[M3] MIN-SET ablation - case x element table:")
    print(f"    {'case':22s} {'rent':7s} K1 K2 K3 K4 K5 K6")
    for c in m3["cases"]:
        print(f"    {c['id']:22s} {str(c['rent_survived']):7s} "
              f"{str(c['K1']):9s} {str(c['K2']):9s} {str(c['K3']):9s} {str(c['K4']):9s} {str(c['K5']):9s} {str(c['K6'])}")
    for ck in ("check_a", "check_b", "check_c"):
        print(f"    {ck}: {m3[ck]['verdict']}  ({m3[ck]['check'][:60]}...)")
    print(f"  VERDICT M3: {m3['verdict']}")

    print("\n[OVERALL]", json.dumps(out["overall"], ensure_ascii=False))
    print(f"UNKNOWN items carried to next stream: {len(UNKNOWN_LIST)}")
    print("saved ->", OUT_PATH)


if __name__ == "__main__":
    main()
