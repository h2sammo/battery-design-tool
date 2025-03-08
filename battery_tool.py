import streamlit as st
import pandas as pd
import plotly.express as px

# Default values for all input parameters
default_values = {
    "areal_capacity": 6.0,
    "cam_mass_loading": 27.0,
    "cam_wt_percent": 93.0,
    "layer": 100.0,
    "mat_thickness": 60.0,
    "polymer_wt_sep": 100.0,
    "li_salt_wt_sep": 0.0,
    "ceramic_wt_sep": 0.0,
    "thickness_sep": 15.0,
    "porosity_sep": 45.0,
    "cell_layers": 15,
    "cell_voltage": 3.85,
    "single_layer_area": 54.0,
    "li_foil_thickness": 30.0,
    "discharged_mat_loading": 2.982816,
    "cell_laminate_pouch_thickness": 88.0,
}

# Constants
polymer_density = 1.7
li_salt_density = 1.33
ceramic_density = 5.61
li_density = 0.534
liquid_electrolyte_density = 1.2
mg_per_mah = 1.38
al_foil_loading = 2.89
al_laminate_pouch_loading = 58.0
al_tab_loading = 8.75
ni_tab_loading = 30.0

# Streamlit UI
st.title("Battery Design Tool")

# Two-column layout
col1, col2 = st.columns([2, 3])

# Input Parameters (Left Column)
with col1:
    st.subheader("Input Parameters")

    with st.expander("Cathode Parameters", expanded=True):
        areal_capacity = st.number_input("Areal Capacity (mAh/cm²)", min_value=0.0, value=default_values["areal_capacity"])
        cam_mass_loading = st.number_input("CAM Mass Loading (mg/cm²)", min_value=0.0, value=default_values["cam_mass_loading"])
        cam_wt_percent = st.number_input("CAM Weight Percentage (%)", min_value=0.0, max_value=100.0, value=default_values["cam_wt_percent"])
        layer = st.number_input("Layer Thickness (μm)", min_value=0.0, value=default_values["layer"])

    with st.expander("Anode Parameters", expanded=False):
        mat_thickness = st.number_input("Mat Thickness (μm)", min_value=0.0, value=default_values["mat_thickness"])
        li_foil_thickness = st.number_input("Li Foil Thickness (μm)", min_value=0.0, value=default_values["li_foil_thickness"])

    with st.expander("Separator Parameters", expanded=False):
        polymer_wt_sep = st.number_input("Polymer Weight (%)", min_value=0.0, max_value=100.0, value=default_values["polymer_wt_sep"])
        li_salt_wt_sep = st.number_input("Li Salt Weight (%)", min_value=0.0, max_value=100.0, value=default_values["li_salt_wt_sep"])
        ceramic_wt_sep = st.number_input("Ceramic Weight (%)", min_value=0.0, max_value=100.0, value=default_values["ceramic_wt_sep"])
        thickness_sep = st.number_input("Thickness (μm)", min_value=0.0, value=default_values["thickness_sep"])
        porosity_sep = st.number_input("Porosity (%)", min_value=0.0, max_value=100.0, value=default_values["porosity_sep"])

    with st.expander("Pouch Cell Parameters", expanded=True):
        cell_layers = st.number_input("Cell Layers", min_value=1, value=default_values["cell_layers"])
        cell_voltage = st.number_input("Cell Voltage (V)", min_value=0.0, value=default_values["cell_voltage"])
        single_layer_area = st.number_input("Single Layer Area (cm²)", min_value=0.0, value=default_values["single_layer_area"])

# Calculate Metrics
def calculate_metrics(areal_capacity, cam_mass_loading, cam_wt_percent, layer, mat_thickness,
                      polymer_wt_sep, li_salt_wt_sep, ceramic_wt_sep, thickness_sep, porosity_sep,
                      cell_layers, cell_voltage, single_layer_area, li_foil_thickness):
    # Use default values for removed parameters
    discharged_mat_loading = default_values["discharged_mat_loading"]
    cell_laminate_pouch_thickness = default_values["cell_laminate_pouch_thickness"]
    
    # Convert percentages to fractions
    polymer_wt_frac = polymer_wt_sep / 100.0
    li_salt_wt_frac = li_salt_wt_sep / 100.0
    ceramic_wt_frac = ceramic_wt_sep / 100.0
    porosity_frac = porosity_sep / 100.0

    # Capacity (Ah)
    capacity = (areal_capacity * single_layer_area * 2 * cell_layers) / 1000

    # Cell Thickness (mm)
    total_layer_thickness = 2 * (layer + mat_thickness + thickness_sep) * cell_layers  # in μm
    li_foil_total_thickness = li_foil_thickness * (cell_layers + 1)  # in μm
    pouch_total_thickness = 2 * cell_laminate_pouch_thickness  # in μm
    cell_thickness = (total_layer_thickness + li_foil_total_thickness + pouch_total_thickness) / 1000  # in mm

    # Cell Volume (cm³) with corrected factor
    cell_volume = single_layer_area * (cell_thickness / 10) * 1.282

    # Separator Mass Loading (mg/cm²)
    separator_density = (polymer_wt_frac * polymer_density + li_salt_wt_frac * li_salt_density + ceramic_wt_frac * ceramic_density)
    mass_loading_sep = (separator_density * thickness_sep * (1 - porosity_frac)) / 10

    # Cathode Layer Weight (g)
    if cam_wt_percent > 0:
        total_cathode_mass_loading_per_side = cam_mass_loading / (cam_wt_percent / 100)
    else:
        total_cathode_mass_loading_per_side = 0
    cathode_layer_weight = (total_cathode_mass_loading_per_side * single_layer_area * 2 * cell_layers) / 1000

    # Anode Weight (g)
    anode_weight = discharged_mat_loading * single_layer_area * cell_layers * 2 / 1000

    # Separator Weight (g)
    separator_weight = mass_loading_sep * single_layer_area * cell_layers * 2 / 1000

    # Other weights (g)
    lithium_foil_weight = (li_foil_thickness * li_density / 10) * single_layer_area * (cell_layers + 1) / 1000
    al_foil_weight = al_foil_loading * single_layer_area * cell_layers / 1000
    al_laminate_pouch_weight = al_laminate_pouch_loading * single_layer_area / 1000
    al_tab_weight = al_tab_loading * single_layer_area / 1000
    ni_tab_weight = ni_tab_loading * single_layer_area / 1000
    liquid_electrolyte_weight = mg_per_mah * capacity * 1000 / 1000

    # Total Cell Weight (g)
    cell_weight = (lithium_foil_weight + cathode_layer_weight + separator_weight + anode_weight +
                   al_foil_weight + al_laminate_pouch_weight + al_tab_weight + ni_tab_weight +
                   liquid_electrolyte_weight)

    # Energy Densities
    if cell_weight > 0:
        g_energy_d = (cell_voltage * capacity / cell_weight) * 1000  # Wh/kg
    else:
        g_energy_d = 0
    if cell_volume > 0:
        v_energy_d = (cell_voltage * capacity / cell_volume) * 1000  # Wh/l
    else:
        v_energy_d = 0

    return capacity, g_energy_d, v_energy_d

# Get metrics
capacity, g_energy_d, v_energy_d = calculate_metrics(
    areal_capacity, cam_mass_loading, cam_wt_percent, layer, mat_thickness,
    polymer_wt_sep, li_salt_wt_sep, ceramic_wt_sep, thickness_sep, porosity_sep,
    cell_layers, cell_voltage, single_layer_area, li_foil_thickness
)

# Output Metrics and Visualization (Right Column)
with col2:
    st.subheader("Output Metrics")
    st.markdown(f'<p style="color:red">Capacity (Ah): {capacity:.2f}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:red">Gravimetric Energy Density (Wh/kg): {g_energy_d:.2f}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:red">Volumetric Energy Density (Wh/l): {v_energy_d:.2f}</p>', unsafe_allow_html=True)

    st.subheader("Performance Metrics Visualization")
    metrics_df = pd.DataFrame({
        "Metric": ["Capacity (Ah)", "Gravimetric Energy Density (Wh/kg)", "Volumetric Energy Density (Wh/l)"],
        "Value": [capacity, g_energy_d, v_energy_d]
    })
    fig = px.bar(metrics_df, x="Metric", y="Value", title="Battery Performance Metrics")
    st.plotly_chart(fig, use_container_width=True)

# Instructions
st.write("Adjust the input values on the left to see how the battery metrics change!")