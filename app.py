import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
from graph.core import CityGraph
from graph.visualization import visualize_graph, visualize_on_map
from graph.algorithms import dijkstra, yen_k_shortest_paths
from utils.helpers import initialize_sample_city, generate_route_summary
from utils.constants import SAMPLE_INTERSECTIONS

def load_css():
    """Load custom CSS styles"""
    st.markdown("""
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --secondary: #6b7280;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #ef4444;
            --info: #06b6d4;
            --light: #f9fafb;
            --dark: #111827;
            --text: #000000;
            --card-bg: #ffffff;
            --border: #e5e7eb;
        }
        
        /* Rest of your CSS styles... */
                :root {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --secondary: #6b7280;
    --success: #16a34a;
    --warning: #d97706;
    --danger: #ef4444;
    --info: #06b6d4;
    --light: #f9fafb;
    --dark: #111827;
    --text: #000000;
    --card-bg: #ffffff;
    --border: #e5e7eb;
}

body {
    color: var(--text);
    background-color: var(--light);
}

.main {
    padding: 1rem 2rem;
}

.sidebar .sidebar-content {
    background-color: var(--card-bg);
    border-right: 1px solid var(--border);
}

.stButton>button {
    border-radius: 8px;
    padding: 0.75rem 1.25rem;
    font-weight: 600;
}

.stButton>button.primary {
    background-color: var(--primary);
    color: white;
}

.stButton>button.primary:hover {
    background-color: var(--primary-hover);
}

.stAlert {
    border-radius: 8px;
}

.stExpander {
    background-color: var(--card-bg);
    border-radius: 8px;
    border: 1px solid var(--border);
}

.header {
    color: var(--dark);
    font-weight: 700;
}

.subheader {
    color: var(--primary);
    font-weight: 600;
}

.folium-map {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    margin-bottom: 1rem !important;
}

.route-container {
    background-color: var(--card-bg) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'city_graph' not in st.session_state:
        st.session_state.city_graph = initialize_sample_city()
        st.session_state.paths = None
        st.session_state.search_params = None

def render_sidebar():
    """Render the sidebar controls"""
    st.sidebar.markdown("<h1 class='header'>🚦 Route Controls</h1>", unsafe_allow_html=True)
    
    
    st.sidebar.markdown("<h2 class='subheader'>Route Settings</h2>", unsafe_allow_html=True)
        
    cols = st.sidebar.columns(2)
    with cols[0]:
        start_node = st.selectbox("📍 Start Location", SAMPLE_INTERSECTIONS, index=0)
    with cols[1]:
        end_node = st.selectbox("🏁 Destination", SAMPLE_INTERSECTIONS, index=5)
        
    time_of_day = st.sidebar.selectbox(
            "🕒 Time of Day",
            ["morning", "afternoon", "evening", "night"],
            index=1
        )
        
    use_case = None
        
    show_multiple_routes = st.sidebar.checkbox("Show alternative routes", True)
    if show_multiple_routes:
        num_routes = st.sidebar.slider("Number of routes to show", 1, 5, 3)
        
        st.sidebar.markdown("---")
        find_route = st.sidebar.button("🔍 FIND BEST ROUTE", use_container_width=True, type="primary")
        st.sidebar.markdown("---")
        
        if find_route:
            with st.spinner("Finding optimal routes..."):
                if show_multiple_routes:
                    paths = yen_k_shortest_paths(
                        st.session_state.city_graph, start_node, end_node, 
                        num_routes, time_of_day, use_case
                    )
                else:
                    dist, path = dijkstra(
                        st.session_state.city_graph, start_node, end_node, 
                        time_of_day, use_case
                    )
                    paths = [(dist, path)] if path else []
                
                st.session_state.paths = paths
                st.session_state.search_params = (
                    start_node, end_node, time_of_day, use_case,
                    show_multiple_routes, num_routes if show_multiple_routes else 1
                )
                
                if not paths:
                    st.error("No path found between the selected locations")

def render_main_content():
    """Render the main content area"""
    st.markdown("<h1 class='header'>Smart Traffic Routing System</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        render_network_visualization()
        if st.session_state.paths:
            render_route_options()
    
    with col2:
        render_traffic_information()

def render_network_visualization():
    """Render the city network visualization"""
    st.markdown("<h2 class='subheader'>City Road Network</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        if st.session_state.paths:
            img = visualize_graph(
                st.session_state.city_graph,
                st.session_state.paths[0][1],
                st.session_state.search_params[2] if st.session_state.search_params else None
            )
            st.image(img, use_container_width=True)
        else:
            img = visualize_graph(st.session_state.city_graph)
            st.image(img, use_container_width=True)
            st.info("Select locations and click 'FIND BEST ROUTE' to see path options")

def render_route_options():
    """Render the available route options"""
    paths = st.session_state.paths
    st.markdown("<h2 class='subheader'>Recommended Routes</h2>", unsafe_allow_html=True)
    
    for i, (dist, path) in enumerate(paths):
        with st.expander(f"Route Option {i+1}: {dist:.1f} minutes", expanded=(i==0)):
            with st.container(border=True):
                st.markdown(f"""
                <div style="color: black;">
                    <p style="font-weight:600;">🚏 <strong>Route Summary:</strong> {path[0]} → ... → {path[-1]}</p>
                    <p style="font-weight:600;">⏱️ <strong>Total Time:</strong> {dist:.1f} minutes</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<p style='font-weight:600; color: black;'>🛣️ <strong>Detailed Path:</strong></p>", unsafe_allow_html=True)
            
            for j in range(len(path)-1):
                u = path[j]
                v = path[j+1]
                weight = _get_route_segment_weight(st.session_state.city_graph, u, v)
                
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="color: black;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight:600;">📍 {u}</span>
                            <span style="font-weight:600;">⏱️ {weight:.1f} min</span>
                            <span style="font-weight:600;">📍 {v}</span>
                        </div>
                        <div style="width:100%; height:6px; background:#e5e7eb; border-radius:3px; margin-top:0.5rem;">
                            <div style="width:{min(weight*3, 100)}%; height:100%; background:#1E40AF; border-radius:3px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<p style='font-weight:600; color: black;'>🗺️ <strong>Map View:</strong></p>", unsafe_allow_html=True)
            with st.container(border=True):
                m = visualize_on_map(st.session_state.city_graph, path)
                folium_static(m, height=250)

def _get_route_segment_weight(city_graph, u, v):
    """Get weight for a route segment considering all factors"""
    weight = city_graph.graph[u][v]['weight']
    
    if st.session_state.search_params and st.session_state.search_params[2]:  # time_of_day
        time_of_day = st.session_state.search_params[2]
        if (u, v) in city_graph.time_weights:
            weight = city_graph.time_weights[(u, v)][time_of_day]
    
    if (u, v) in city_graph.user_reports:
        weight += city_graph.user_reports[(u, v)]
    
    return weight

def render_traffic_information():
    """Render the traffic information panel"""
    st.markdown("<h2 class='subheader'>Traffic Information</h2>", unsafe_allow_html=True)
    city_graph = st.session_state.city_graph
    
    with st.expander("🚦 Live Traffic Conditions", expanded=True):
        if city_graph.traffic_alerts:
            st.warning("**Traffic Alerts**")
            for u, v in city_graph.traffic_alerts:
                st.write(f"⚠ High congestion between {u} and {v}")
        
        if city_graph.congestion_zones:
            st.error("**Congestion Zones**")
            for u, v in city_graph.congestion_zones:
                st.write(f"🚧 Congestion zone: {u} ↔ {v}")
        
        if city_graph.user_reports:
            st.info("**User Reports**")
            for (u, v), delay in city_graph.user_reports.items():
                st.write(f"📢 +{delay} min delay between {u} and {v}")
        
        if not (city_graph.traffic_alerts or city_graph.congestion_zones or city_graph.user_reports):
            st.success("✅ No current traffic issues reported")

def main():
    """Main application entry point"""
    st.set_page_config(
        layout="wide",
        page_title="🚦 Smart Traffic Routing",
        page_icon="🚦",
        initial_sidebar_state="expanded"
    )
    
    load_css()
    initialize_session_state()
    render_sidebar()
    render_main_content()

if __name__ == "__main__":
    main()