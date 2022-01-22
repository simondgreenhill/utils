# Patrick Baylis' code
# downloaded from
# https://www.patrickbaylis.com/blog/2020-02-28-specification-curve/
# on 3/22/21
# Edited by Simon Greenhill, sgreenhill@berkeley.edu

# Create sensitivity curve of coefficient estimates
pacman::p_load(tidyverse, cowplot, fastDummies)

# Setup ----
theme_set(theme_cowplot())

# plot coefficients
make_coef_plot = function(estimates, order=NULL, n_per_group=NULL) {
    if (is.null(order)) {
        estimates$order = seq(1, nrow(estimates))
        order = quo(order)
    }
    
    
    coef_plot <- ggplot(estimates, aes(x = !!order, y = est)) +
        geom_linerange(aes(ymin = ci_l, ymax = ci_h), size = 1, alpha = 0.5) +
        geom_point(fill = "white", shape = 21) +
        geom_hline(yintercept = 0, alpha=0.5) +
        labs(y = "Coefficient") +
        theme_minimal() +
        theme(axis.title.x = element_blank(), axis.ticks.x = element_blank(),
              axis.line.x = element_blank(), axis.text.x = element_blank(),
        )
    
    if (!is.null(n_per_group)) {
        n_est = nrow(estimates)
        coef_plot = coef_plot + 
            scale_x_continuous(minor_breaks = seq(0.3, n_est, n_per_group),
                               breaks = NULL)
    }
    
    return(coef_plot)    
}

# Function to create a specification plot for a single category. 
make_spec_plot <- function(estimates, category, order, n_per_group=NULL) {
    specs <- dummy_cols(estimates,
                        select_columns = category,
                        remove_selected_columns = T) %>%
        select(!!order, starts_with(category)) %>% 
        pivot_longer(starts_with(category), names_prefix = paste0(category, "_")) %>%
        mutate(name = factor(name, levels = rev(unique(name))))
    
    spec_plot <- ggplot(specs, aes(x = !!order, y = name, alpha = value)) +
        geom_point() + 
        theme_minimal() +
        scale_alpha_continuous(guide = FALSE) +
        theme(axis.title.x = element_blank(),
              axis.ticks.x = element_blank(),
              axis.line.x = element_blank(),
              axis.text.x = element_blank(),
              axis.text.y = element_text(size = 10),
              axis.title.y = element_blank(),
              axis.ticks.y = element_blank(),
              axis.line.y = element_blank())
    
    if (!is.null(n_per_group)) {
        n_est = nrow(estimates)
        spec_plot = spec_plot + 
            scale_x_continuous(minor_breaks = seq(0.3, n_est, n_per_group),
                               breaks = NULL)
    }
    
    return(spec_plot)    
}

# function to create combined coefficients and specifications array
make_spec_chart = function(estimates, categories, order=NULL, n_per_group=NULL) {
    #' order: quasiquotation (name of order column). default: NULL
    #' n_per_group: number of specifications between gridlines
    if (is.null(order)) {
        estimates$order = seq(1, nrow(estimates))
        order = quo(order)
    }
    
    coefs = make_coef_plot(estimates, order, n_per_group)
    specs = lapply(categories, make_spec_plot, estimates=estimates, order=order,
                   n_per_group)
    
    # calculate relative heights based on levels of each category
    n_cats = sapply(categories, function(x) length(unique(estimates[, x]))) + 1
    hts = n_cats / (sum(n_cats) + length(categories))
    combined = plot_grid(plotlist = c(list(coefs), specs), 
                         labels = c("", categories),
                         label_size = 10,
                         label_fontface = "italic",
                         vjust = 0.5,
                         hjust = -0.1,
                         rel_heights = c(1, hts),
                         ncol = 1,
                         align = "v")
    return(combined)
}