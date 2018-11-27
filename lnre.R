## see: http://zipfr.r-forge.r-project.org
library(zipfR)

args <- commandArgs(trailingOnly = TRUE)
filein <- args[1]
#print(paste('Evaluating Zipfian-ness of', filein))

## fit Zipfian model to frequency spectrum of given type frequency list
tfl <- read.tfl(filein)
#print(tfl)
spc <- tfl2spc(tfl)
#print(spc)
#fzm <- lnre('fzm', spc, cost='chisq')
zm <- lnre('zm', spc, cost='chisq')
#print(summary(fzm))
# print alpha parameter, GoF chi-sq and p
output <- c(zm$param$alpha, zm$gof$X2, zm$gof$p)
df.out <- data.frame(output)
write.table(df.out, '~/tmp/lnre.txt', sep='\t', row.names=F, col.names=F)

## make plot
#fzm.spc <- lnre.spc(fzm, N(fzm))
#plotfile <- gsub('(_freqlist\\.|\\.)txt$', '_histogram.pdf', filein, perl=T)
#pdf(plotfile)
#plot(spc, fzm.spc, legend=c("observed", "fZM"))
#dev.off()
#system(paste('open', plotfile))
#print(paste('Plot saved to', plotfile))
