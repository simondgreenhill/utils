pacman::p_load(tigris, rnaturalearth, ggplot2, sf)

make_us_base_map = function(admin_boundaries=states) {
    #' Function that produces a base map with the Great Lakes and admin 
    #' boundaries.
    #' To specify admin boundaries, pass the name of a tigris function
    shp = states() %>%
        # continental US only
        filter(!(STATEFP %in% c("02", "15", "60", "66", "69", "72", "78"))) %>%
        st_transform(crs="WGS84") # to match X and Y in data, which are in WGS84
    
    # great lakes
    lakes = ne_download(scale=110, type="lakes", category="physical") %>%
        st_as_sf() %>%
        st_transform(crs="WGS84") %>%
        filter(name %in% c('Lake Superior', 'Lake Erie', 'Lake Michigan', 'Lake Huron'))
    
    base_map = ggplot() + 
        geom_sf(data=shp, color="grey", fill="white ", lwd=0.1) +
        geom_sf(data=lakes, fill="white", color="grey", lwd=0.1) + 
        theme_bw() +
        theme(
            panel.border = element_blank(),
            panel.grid.major = element_blank(),
            panel.grid.minor = element_blank(),
            axis.line=element_blank(),
            axis.ticks = element_blank(),
            axis.title = element_blank(),
            axis.text = element_blank(),
            legend.position='bottom'
        )
    
    return(base_map)    
}
