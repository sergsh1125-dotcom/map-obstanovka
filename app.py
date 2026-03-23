# ===============================
# 5. ПУЛЬТ УПРАВЛІННЯ (ОНОВЛЕНИЙ)
# ===============================
st.header("☢️ КАРТА РХБ ОБСТАНОВКИ")

col_map, col_gui = st.columns([3, 1])

with col_gui:
    st.subheader("ПУЛЬТ УПРАВЛІННЯ")

    # ===== Координати =====
    if st.session_state.clicked_coords:
        c_lat, c_lon = st.session_state.clicked_coords['lat'], st.session_state.clicked_coords['lng']
        st.write(f"Вибрано: {c_lat:.6f}, {c_lon:.6f}")

        c1, c2 = st.columns(2)
        if c1.button("Вставити координати у форму"):
            st.session_state.manual_lat = c_lat
            st.session_state.manual_lon = c_lon
            # Ми НЕ видаляємо clicked_coords тут, щоб бачити де точка, 
            # але форма тепер підхопить значення
            st.rerun()

        if c2.button("Виключити маркер"):
            st.session_state.clicked_coords = None
            st.rerun()

    st.divider()

    # ===== Вибір типу (з ключем для стабільності) =====
    data_type = st.radio(
        "Тип забруднення",
        ["радіоактивне забруднення", "хімічне забруднення"],
        key="selected_pollution_type" 
    )

    # ===== Точка вимірювання =====
    st.markdown("### Точка вимірювання")

    l1 = st.number_input("Широта", format="%.6f", value=st.session_state.get('manual_lat', 50.4501))
    l2 = st.number_input("Довгота", format="%.6f", value=st.session_state.get('manual_lon', 30.5234))

    # ===== Речовина (Відображається тільки для хімії, стан зберігається через key) =====
    substance = ""
    if data_type == "хімічне забруднення":
        substance = st.text_input("Назва речовини", key="substance_name_input")

    # ===== Значення =====
    val = st.number_input("Значення концентрації/ПЕД", step=0.01, format="%.2f", key="measurement_value")

    # ===== Одиниці (з ключем) =====
    if data_type == "радіоактивне забруднення":
        uni = st.selectbox("Одиниця", ["мкЗв/год", "мЗв/год"], key="radio_units")
    else:
        uni = st.selectbox("Одиниця", ["мг/м³"], key="chem_units")

    tim = st.date_input("Дата вимірювання", value=datetime.now()).strftime("%d.%m.%Y")

    if st.button("Нанести на карту", use_container_width=True):
        # Беремо назву речовини з session_state, якщо це хімія
        current_substance = st.session_state.get("substance_name_input", "") if data_type == "хімічне забруднення" else ""
        
        new_row = pd.DataFrame([{
            "lat": l1,
            "lon": l2,
            "value": val,
            "unit": uni,
            "time": tim,
            "type": data_type,
            "substance": current_substance
        }])

        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        # Очищуємо поле речовини після успішного нанесення, якщо потрібно
        if "substance_name_input" in st.session_state:
            st.session_state["substance_name_input"] = ""
        st.rerun()

    st.divider()
    # ... далі ваш код імпорту CSV без змін ...
