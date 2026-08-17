"""
Jyotish practice console. Run with: streamlit run app.py
"""

from datetime import datetime, date, time
from zoneinfo import ZoneInfo

import streamlit as st

from jyotish import db, render, varga
from jyotish.dasha import current_dasha, vimshottari, balance_at_birth
from jyotish.engine import (
    AYANAMSAS, SIGNS, BirthData, compute_chart, overlay, sade_sati, transits,
)

st.set_page_config(page_title="Jyotish.ai", layout="wide")

conn = db.connect()


def birth_form(prefill: BirthData | None = None) -> BirthData | None:
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Name", value=prefill.name if prefill else "")
        d = st.date_input(
            "Date of birth",
            value=date(prefill.year, prefill.month, prefill.day) if prefill else date(1990, 1, 1),
            min_value=date(1800, 1, 1), max_value=date(2100, 1, 1),
        )
        t = st.time_input(
            "Time of birth",
            value=time(prefill.hour, prefill.minute) if prefill else time(12, 0),
            step=60,
        )
    with c2:
        place = st.text_input("Place", value=prefill.place if prefill else "")
        lat = st.number_input("Latitude", value=prefill.latitude if prefill else 28.6139, format="%.4f")
        lon = st.number_input("Longitude", value=prefill.longitude if prefill else 77.2090, format="%.4f")
        ayan = st.selectbox("Ayanamsa", list(AYANAMSAS), index=0)

    if not name:
        return None
    return BirthData(
        name=name, year=d.year, month=d.month, day=d.day,
        hour=t.hour, minute=t.minute, latitude=lat, longitude=lon,
        place=place, ayanamsa=ayan,
    )


tab_chart, tab_clients, tab_search = st.tabs(["Chart", "Clients", "Search notes"])

with tab_clients:
    st.subheader("Saved charts")
    rows = db.list_clients(conn)
    if rows:
        pick = st.selectbox(
            "Open a client",
            options=[r["id"] for r in rows],
            format_func=lambda i: next(
                f'{r["name"]}  ({r["place"]}, {r["day"]}/{r["month"]}/{r["year"]})'
                for r in rows if r["id"] == i
            ),
        )
        if st.button("Load into chart tab"):
            st.session_state["birth"] = db.load_client(conn, pick)
            st.session_state["client_id"] = pick
            st.rerun()
    else:
        st.caption("Nothing saved yet.")

with tab_search:
    q = st.text_input("Full text search across every reading you have written")
    if q:
        for r in db.search_readings(conn, q):
            st.markdown(f"**{r['client_name']}** · {r['session_date']} · {r['dasha_context']}")
            st.write(r["body"])
            st.divider()

with tab_chart:
    birth = birth_form(st.session_state.get("birth"))

    if birth:
        chart = compute_chart(birth)
        now = datetime.now(ZoneInfo(birth.resolve_tz()))
        moving = transits(now, birth.ayanamsa)
        chain = current_dasha(chart, now)
        ss = sade_sati(chart, moving)

        left, right = st.columns([1, 1])

        with left:
            style = st.radio("Style", ["North Indian", "South Indian"], horizontal=True)
            v = st.selectbox("Varga", list(varga.VARGAS), index=0)
            show_transit = st.checkbox("Overlay current transits", value=False)

            vs = varga.varga_chart(chart, v) if v != "D1 Rasi" else None
            tsigns = {n: g.sign for n, g in moving.items()} if show_transit else None

            svg = (render.north_indian(chart, vs, transit_signs=tsigns)
                   if style == "North Indian"
                   else render.south_indian(chart, vs))
            st.markdown(svg, unsafe_allow_html=True)

        with right:
            st.markdown(f"**Lagna** {SIGNS[chart.lagna_sign]} · "
                        f"{chart.ascendant % 30:.2f}° · "
                        f"ayanamsa {chart.ayanamsa_value:.4f}°")

            st.dataframe(
                [
                    {
                        "Graha": g.name,
                        "Sign": g.sign_name,
                        "Deg": round(g.degree_in_sign, 2),
                        "House": g.house,
                        "Nakshatra": f"{g.nakshatra_name} {g.pada}",
                        "R": "R" if g.retrograde else "",
                        "Comb": "C" if g.combust else "",
                        "Dignity": g.dignity,
                    }
                    for g in chart.grahas.values()
                ],
                hide_index=True, use_container_width=True,
            )

            lord, bal = balance_at_birth(chart)
            st.caption(f"Dasha balance at birth: {lord} {bal:.2f} years")
            st.markdown("**Running dasha**  \n" + " → ".join(
                f"{p.lord} ({p.start:%d %b %Y} to {p.end:%d %b %Y})" for p in chain
            ))

            if ss["active"]:
                st.warning(f"Sade Sati: {ss['phase']}. Natal Moon in "
                           f"{ss['moon_sign']}, Saturn in {ss['saturn_sign']}.")
            elif ss["dhaiya"]:
                st.info("Saturn dhaiya active (ashtama or kantaka).")

            vg = varga.vargottama(chart)
            if vg:
                st.caption("Vargottama: " + ", ".join(vg))

        st.divider()
        st.subheader("Reading notes")
        cid = st.session_state.get("client_id")
        if cid is None:
            if st.button("Save this chart to practice"):
                st.session_state["client_id"] = db.save_client(conn, birth)
                st.rerun()
        else:
            for r in db.readings_for(conn, cid):
                with st.expander(f"{r['session_date']} · {r['dasha_context']}"):
                    st.write(r["body"])

            note = st.text_area("New note", height=200,
                                placeholder="Observations, what was discussed, what to watch for next.")
            if st.button("Save note") and note.strip():
                db.save_reading(
                    conn, cid, note,
                    dasha_context=" / ".join(p.lord for p in chain),
                    transit_context=", ".join(
                        f"{n} {SIGNS[g.sign]}" for n, g in moving.items()
                    ),
                )
                st.rerun()
