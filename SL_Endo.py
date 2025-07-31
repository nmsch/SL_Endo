#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st

# --- Tooth Selector as grid ---
def select_tooth():
    st.markdown("### Select tooth to evaluate")
    type_select = st.radio("Tooth Type:", ["Permanent", "Primary", "Region"], horizontal=True)
    selected = None

    if type_select == "Permanent":
        permanent = [str(i) for i in range(1, 33)]
        rows = 4
        cols = 8
        for row in range(rows):
            cols_ = permanent[row*cols:(row+1)*cols]
            cols_buttons = st.columns(len(cols_))
            for i, num in enumerate(cols_):
                if cols_buttons[i].button(num, key=f"perm_{num}"):
                    st.session_state["tooth"] = num
                    st.session_state["tooth_type"] = "Permanent"
                    st.session_state["page"] = "chief"
                    st.experimental_rerun()
    elif type_select == "Primary":
        primary = [chr(i) for i in range(65, 85)]  # A-T
        rows = 4
        cols = 5
        for row in range(rows):
            cols_ = primary[row*cols:(row+1)*cols]
            cols_buttons = st.columns(len(cols_))
            for i, let in enumerate(cols_):
                if cols_buttons[i].button(let, key=f"prim_{let}"):
                    st.session_state["tooth"] = let
                    st.session_state["tooth_type"] = "Primary"
                    st.session_state["page"] = "chief"
                    st.experimental_rerun()
    else:
        regions = [
            "Upper left", "Upper right",
            "Lower left", "Lower right",
            "Maxillary anteriors", "Mandibular anteriors", "Unknown"
        ]
        for r in regions:
            if st.button(r, key=f"region_{r}"):
                st.session_state["tooth"] = r
                st.session_state["tooth_type"] = "Region"
                st.session_state["page"] = "chief"
                st.experimental_rerun()

def chief_complaint_screen():
    st.markdown(f"### Tooth: {st.session_state['tooth']}")
    cc = st.text_area("Chief Complaint (optional):", key="chief_complaint")
    if st.button("Next: Pulpal Symptoms"):
        st.session_state["chief"] = cc
        st.session_state["page"] = "pulpal"
        st.experimental_rerun()

def pulpal_screen():
    st.markdown(f"### Pulpal Symptoms — Tooth {st.session_state['tooth']}")
    opts = [
        "Sensitive to cold but resolves quickly",
        "Sensitive to cold and lingers (≥30s)",
        "Sensitive to hot and lingers (≥30s)",
        "No response to cold",
        "No sensitivity to hot or cold",
        "Sensitive to sweets"
    ]
    pulpal = []
    for o in opts:
        if st.checkbox(o, key="pulp_"+o):
            pulpal.append(o)
    if st.button("Next: Periapical Symptoms"):
        st.session_state["pulpal"] = pulpal
        st.session_state["page"] = "periapical"
        st.experimental_rerun()

def periapical_screen():
    st.markdown(f"### Periapical Symptoms — Tooth {st.session_state['tooth']}")
    opts = [
        "Sensitive to biting",
        "Sensitive to percussion",
        "Sensitive to palpation",
        "Facial swelling",
        "Sinus tract ('bump on gums')",
        "No symptoms but radiolucency on Xrays"
    ]
    periapical = []
    for o in opts:
        if st.checkbox(o, key="peri_"+o):
            periapical.append(o)

    # Red flag
    pulpal_resp = any(s in st.session_state.get("pulpal", []) for s in [
        "Sensitive to cold but resolves quickly",
        "Sensitive to cold and lingers (≥30s)",
        "Sensitive to hot and lingers (≥30s)",
        "Sensitive to sweets"
    ])
    swelling = "Facial swelling" in periapical
    sinus = "Sinus tract ('bump on gums')" in periapical
    if (swelling or sinus) and pulpal_resp:
        msg = "Red flag: Pulpal diagnosis inconsistent with periapical findings. Recommend repeat testing."
        st.error(msg)

    if st.button("Next: Additional Tests"):
        st.session_state["periapical"] = periapical
        st.session_state["page"] = "additional"
        st.experimental_rerun()

def additional_tests_screen():
    st.markdown("### Additional Testing")
    dprob = st.checkbox("Any deep or narrow probings?")
    dtext = st.text_input("If probing, details (e.g. 8mm buccal pocket):")
    bstick = st.checkbox("Bite stick positive?")
    btext = st.text_input("If yes, which cusp(s)?")
    caries = st.checkbox("Caries present?")
    cariest = st.text_input("If yes, where?")
    recent = st.checkbox("Recent dental work?")
    recentt = st.text_input("If yes, when?")
    mast = st.checkbox("Discomfort with muscles of mastication?")
    mastt = st.text_input("Which muscles/side?")
    occ = st.text_area("Occlusion description:")

    if st.button("Show Summary & Recommendation"):
        st.session_state["probing"] = dprob
        st.session_state["probing_detail"] = dtext
        st.session_state["bite_stick"] = bstick
        st.session_state["bite_stick_detail"] = btext
        st.session_state["caries"] = caries
        st.session_state["caries_detail"] = cariest
        st.session_state["recent"] = recent
        st.session_state["recent_detail"] = recentt
        st.session_state["mast"] = mast
        st.session_state["mast_detail"] = mastt
        st.session_state["occlusion"] = occ
        st.session_state["page"] = "summary"
        st.experimental_rerun()

def treatment_recommendations(pulpal, periapical, caries, probing_detail, bite_stick, previously_treated, radiolucency, symptoms):
    if any([
        "Necrotic pulp" in pulpal,
        "Symptomatic irreversible pulpitis" in pulpal,
        "Asymptomatic irreversible pulpitis" in pulpal
    ]):
        return "Root canal therapy or extraction (with or without replacement)"
    if previously_treated and radiolucency and (
            "Asymptomatic apical periodontitis" in periapical or symptoms):
        return "Endodontic retreatment, apical surgery, or extraction (with or without replacement)"
    if any(x in probing_detail for x in ["5", "6", "7", "8", "9", "10", "11", "12"]):
        return "Open and medicate the tooth to see if symptoms resolve or extraction (with or without replacement)"
    if "Reversible pulpitis" in pulpal:
        if (any(x in probing_detail for x in ["4", "5"]) and bite_stick):
            return "Place temporary crown and re-evaluate in 4–6 weeks"
        return "Caries removal or re-evaluate in 4–6 weeks" if caries else "Re-evaluate in 4–6 weeks"
    return "No specific treatment recommendation based on current findings."

def summary_screen():
    st.markdown("### Case Overview & Diagnosis")
    tooth = st.session_state["tooth"]
    chief = st.session_state.get("chief", "")
    pulpal = st.session_state.get("pulpal", [])
    peri = st.session_state.get("periapical", [])
    # Pulpal diagnosis
    pulpal_diag = "Not determined"
    if any("Symptomatic irreversible" in s for s in pulpal) or "Sensitive to cold and lingers (≥30s)" in pulpal or "Sensitive to hot and lingers (≥30s)" in pulpal:
        pulpal_diag = "Symptomatic irreversible pulpitis"
    elif "Sensitive to cold but resolves quickly" in pulpal:
        pulpal_diag = "Reversible pulpitis"
    elif "Sensitive to sweets" in pulpal:
        pulpal_diag = "Possible reversible pulpitis"
    elif "No response to cold" in pulpal:
        pulpal_diag = "Necrotic pulp or previously treated"
    elif "No sensitivity to hot or cold" in pulpal:
        pulpal_diag = "Normal pulp / Asymptomatic irreversible pulpitis / Previously treated / Necrotic pulp (need more info)"
    # Periapical diagnosis
    d_peri = []
    if "Sensitive to biting" in peri or "Sensitive to percussion" in peri or "Sensitive to palpation" in peri:
        d_peri.append("Symptomatic apical periodontitis")
    if "Facial swelling" in peri:
        d_peri.append("Acute apical abscess (Necrotic pulp required)")
    if "Sinus tract ('bump on gums')" in peri:
        d_peri.append("Chronic apical abscess (Diff: perio abscess or osteosarcoma, biopsy req)")
    if "No symptoms but radiolucency on Xrays" in peri:
        d_peri.append("Asymptomatic apical periodontitis")
    periapical_diag = ', '.join(d_peri) if d_peri else "Not determined"
    st.markdown(f"**Tooth:** {tooth}")
    st.markdown(f"**Chief Complaint:** {chief if chief else 'Not provided'}")
    st.markdown(f"**Pulpal diagnosis:** {pulpal_diag}")
    st.markdown(f"**Periapical diagnosis:** {periapical_diag}")

    # Red flag if mismatch between vital pulp and abscess/sinus tract
    pulpal_resp = any(x in pulpal for x in [
        "Sensitive to cold but resolves quickly",
        "Sensitive to cold and lingers (≥30s)",
        "Sensitive to hot and lingers (≥30s)",
        "Sensitive to sweets"
    ])
    if (("Facial swelling" in peri) or ("Sinus tract ('bump on gums')" in peri)) and pulpal_resp:
        st.error("Red flag: Pulpal diagnosis inconsistent with periapical findings. Recommend repeat testing.")

    st.markdown("**Additional testing notes:**")
    if st.session_state["probing"] and st.session_state["probing_detail"].strip():
        st.markdown(f"- Deep/narrow probings: {st.session_state['probing_detail']}")
    if st.session_state["bite_stick"] and st.session_state["bite_stick_detail"].strip():
        st.markdown(f"- Bite stick positive: {st.session_state['bite_stick_detail']}")
    if st.session_state["caries"] and st.session_state["caries_detail"].strip():
        st.markdown(f"- Caries present: {st.session_state['caries_detail']}")
    if st.session_state["recent"] and st.session_state["recent_detail"].strip():
        st.markdown(f"- Recent dental work: {st.session_state['recent_detail']}")
    if st.session_state["mast"] and st.session_state["mast_detail"].strip():
        st.markdown(f"- Discomfort with muscles of mastication: {st.session_state['mast_detail']}")
    if st.session_state["occlusion"].strip():
        st.markdown(f"- Occlusion: {st.session_state['occlusion']}")
    if not any([
        st.session_state["probing"], st.session_state["bite_stick"], st.session_state["caries"],
        st.session_state["recent"], st.session_state["mast"], st.session_state["occlusion"].strip()]):
        st.markdown("None")

    # Crack/fracture warning
    if st.session_state["probing"] or st.session_state["bite_stick"]:
        st.error("Warning: Deep probing or bite stick positive – Possible crack or fracture present.")

    # Recommendations
    previously_treated = "previously treated" in pulpal_diag or "Necrotic pulp" in pulpal_diag
    radiolucency = ("No symptoms but radiolucency on Xrays" in peri) or ("Asymptomatic apical periodontitis" in periapical_diag)
    any_symptoms = "Sensitive to biting" in peri or "Sensitive to percussion" in peri or "Sensitive to palpation" in peri

    rec = treatment_recommendations(
        pulpal_diag, periapical_diag, st.session_state["caries"],
        st.session_state["probing_detail"], st.session_state["bite_stick"],
        previously_treated, radiolucency, any_symptoms
    )
    st.markdown("**Treatment Recommendation:**")
    st.success(rec)
    st.info("*For clinical decision-making, always corroborate these with full clinical exam and radiographic review.")

# --- App Main Loop ---
if __name__ == "__main__":
    st.set_page_config(page_title="EndoDiagnosis Tool", layout="wide")
    if "page" not in st.session_state: st.session_state["page"] = "tooth"
    st.title("Endodontic Diagnosis Tool")
    st.caption("by Summit Analytics LLC")
    page = st.session_state["page"]

    if page == "tooth":
        select_tooth()
    elif page == "chief":
        chief_complaint_screen()
    elif page == "pulpal":
        pulpal_screen()
    elif page == "periapical":
        periapical_screen()
    elif page == "additional":
        additional_tests_screen()
    elif page == "summary":
        summary_screen()

    st.markdown("---")
    if page != "tooth":
        if st.button("Start Over"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.experimental_rerun()


# In[ ]:




