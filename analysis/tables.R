# This script contains helper functions for making tables using R.

get_robust_se = function(x) {
    #' helper function for getting robust SEs from summary, to be passed to stargazer
    return(coef(summary(x, robust=TRUE))[, 2])
}