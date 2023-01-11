# plot coefficients
plot_event_study = function(reg, ylabel=NULL, caption=NULL) {
    ci = confint(reg)
    coefs = tibble(
        event_time = names(summary(reg)$coefficients),
        coeff = as.vector(summary(reg)$coefficients),
        ci_l = ci[, 1],
        ci_h = ci[, 2]
    ) %>%
        mutate(
            # convert event time to numeric
            event_time = unlist(str_extract_numbers(event_time, negs=T))
        )
    
    plot = ggplot(coefs) +
        geom_vline(aes(xintercept=-1), linetype='dashed', color='red') +
        geom_hline(aes(yintercept=0), color='grey') +
        geom_point(aes(x = event_time, y=coeff)) +
        geom_errorbar(aes(x=event_time, ymin=ci_l, ymax=ci_h)) +
        labs(
            x = 'Event time',
            y = ifelse(is.null(ylabel), 'Point estimate and 95% CI', ylabel),
            caption = ifelse(is.null(caption), '', str_wrap(caption, 100))
        )
    
    return(plot)
}
