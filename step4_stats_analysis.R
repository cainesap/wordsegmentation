## libraries
if (!require("pacman")) install.packages("pacman")
suppressMessages(library(pacman))
pacman::p_load(ggplot2, reshape2, lme4)


## initial stats from step1
stats0 <- read.delim('~/Corpora/CHILDES/corpus_statistics.txt', as.is=T)

## basic stats used throughout
# n.languages
length(unique(stats0$language))
# n.corpora
length(unique(stats0$corpuscollection))
# n.children
length(unique(paste(stats0$corpuscollection, stats0$child)))  # should match nrow(stats0)


## per language stats: Table 1
langs <- unique(stats0$language)
langs <- langs[order(langs)]
for (lang in langs) {
 subs <- subset(stats0, language==lang)
 print(paste("====", lang))
 print(paste('N.collect:', length(unique(subs$corpuscollection))))
 print(paste('N.corpora:', length(unique(subs$child))))
 print(paste('N.partic:', sum(subs$n.participants)))
}


## secondary stats from step3: Table 1 cont'd
stats <- read.csv('~/Corpora/CHILDES/segmentation_experiment_stats.csv', as.is=T)
stats$wordseg <- toupper(stats$wordseg)
stats$language <- paste0(toupper(substring(stats$language, 1, 1)), substring(stats$language, 2))

# token counts for each lang @ 1000 and 10,000 utterances
print('N.utterances: 10,000')
sumTokens <- 0
for (lang in unique(stats$language)) {
  tokenCount <- sum(subset(subset(subset(stats, language==lang), n.utterances==10000), wordseg=='RAND_BASELINE')$tokens)
  sumTokens <- sumTokens + tokenCount
  print(paste(lang, tokenCount))
}
print(paste('TOTAL:', sumTokens))  # total word tokens in all corpora


## eval means for each wordseg model (Table 2)
## at 1000(0) utterances
algos <- unique(stats$wordseg)
ttbcols <- 19:27  # which columns for type, token, boundary.all?
for (nutt in c(1000, 10000)) {
  print(paste(nutt, 'utterances'))
  subs <- subset(stats, n.utterances==nutt)
  for (algo in algos) {
    algo.sub <- subset(subs, wordseg==algo)
    print(paste(algo, 'means'))
    print(colMeans(algo.sub[,ttbcols]))
#    print('standard deviation')
#    print(quantile(unlist(lapply(algo.sub[,ttbcols], sd))))
  }
}

## pairwise stats tests between each model for each F-measure
fCols <- c(21, 24, 27)
for (nutt in c(1000, 10000)) {
  for (c in fCols) {
    print(colnames(stats)[c])
    pvalues <- c()
    for (i in 1:(length(algos)-1)) {
      x.algo <- algos[i]
      x.subs <- subset(subs, wordseg==x.algo)
      y.algos <- algos[(i+1):length(algos)]
      for (y.algo in y.algos) {
        print(paste('Pairwise test between', x.algo, 'and', y.algo))
        y.subs <- subset(subs, wordseg==y.algo)
        tt <- t.test(x.subs[,c], y.subs[,c], alternative='two.sided', var.equal=F)
        pvalues <- append(pvalues, tt$p.value)
        print(tt)
      }
    }
    # apply p adjustment for multiple comparisons: Bonferonni and False Discovery rate
    print('Bonferonni adjustment')
    print(p.adjust(pvalues, method='bon'))
    print('False discovery rate adjustment')
    print(p.adjust(pvalues, method='fdr'))
  }
}


## per language stats for PUDDLE (Table 3)
subs <- subset(subset(stats, n.utterances==10000), wordseg=='PUDDLE')
langs <- unique(stats$language)
lang.df <- data.frame()
colnums <- c(8:13,16,17,19:27)  # TTR, wordlength, boundary prob, eval scores
for (lang in langs) {
  langsub <- subset(subs, language==lang)
  df1 <- data.frame(colMeans(langsub[,colnums]))
  colnames(df1)[1] <- lang
  df2 <- data.frame(t(df1))
  lang.df <- rbind(lang.df, df2)
}
# order by token F: whole thing
fCols <- c(11, 14, 17)
lang.df <- lang.df[with(lang.df, order(-tokenF)),]
print(lang.df)

# F measures only (Table 3)
print(round(lang.df[,fCols], 3))

# how much variation?
print(lapply(lang.df[,fCols], range))
print(lapply(lang.df[,fCols], sd))




## regression models for PUDDLE token F
range01 <- function(x){(x-min(x))/(max(x)-min(x))}  # scale between 0 and 1
puddle <- subset(stats, wordseg=='PUDDLE')
puddle$corpusID <- paste0(puddle$language, '_', puddle$corpus, '_', puddle$child)
puddle$boundary.entropy <- range01(puddle$boundary.entropy)
puddle$zm.X2 <- range01(puddle$zm.X2)
puddle$mean.phones.per.word <- range01(puddle$mean.phones.per.word)

# linear model
mod.lm <- lm(data=puddle, tokenF ~ prop.owus+(TTR*n.utterances)+boundary.entropy+zm.alpha+zm.X2+mean.phones.per.word)
print(summary(mod.lm))
print(AIC(mod.lm))
# mixed-effects
mod.lmer <- lmer(data=puddle, tokenF ~ prop.owus+(TTR*n.utterances)+boundary.entropy+zm.alpha+zm.X2+mean.phones.per.word+(1|corpusID))
print(summary(mod.lmer))
print(AIC(mod.lmer))
print(anova(mod.lmer, mod.lm))  # pass lmer object first


## FIGURES
## plots of type, token, boundary P R F
algos <- unique(stats$wordseg)
subs <- subset(stats, n.utterances==10000)
subs$corpusID <- paste0(subs$language, '_', subs$corpus, '_', subs$child)
submelt <- melt(subs, id.var=c('corpusID', 'wordseg'), measure.var=c('typeF', 'tokenF', 'boundary.all.F'))
submelt$wordseg <- factor(submelt$wordseg, levels=algos)

# boxplot of per model F-measures (Figure 1)
ggplot(submelt, aes(x=variable, y=value)) + geom_boxplot(outlier.alpha=1/4) + facet_wrap(~wordseg) + theme_bw() + theme(text=element_text(family="Times")) + scale_x_discrete('') + scale_y_continuous('', breaks=seq(0, 1, .1)) 



ggplot(stats, aes(x=n.utterances, y=typeP, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()
ggplot(stats, aes(x=n.utterances, y=typeR, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()
ggplot(stats, aes(x=n.utterances, y=typeF, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()

ggplot(stats, aes(x=n.utterances, y=tokenP, group=child)) + geom_line(aes(colour=language)) + scale_x_continuous(breaks=seq(0, 10000, 1000)) + scale_y_continuous('token precision', breaks=seq(0, 1, .1)) + facet_wrap(~wordseg) + theme_bw() + theme(text=element_text(family="Times"))
ggplot(stats, aes(x=n.utterances, y=tokenR, group=child)) + geom_line(aes(colour=language)) + scale_x_continuous(breaks=seq(0, 10000, 1000)) + scale_y_continuous('token recall', breaks=seq(0, 1, .1)) + facet_wrap(~wordseg) + theme_bw() + theme(text=element_text(family="Times"))
ggplot(stats, aes(x=n.utterances, y=tokenF, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()

ggplot(stats, aes(x=n.utterances, y=boundary.all.P, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()
ggplot(stats, aes(x=n.utterances, y=boundary.all.R, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()
ggplot(stats, aes(x=n.utterances, y=boundary.all.F, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()

ggplot(stats, aes(x=n.utterances, y=boundary.noedge.P, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()
ggplot(stats, aes(x=n.utterances, y=boundary.noedge.R, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()
ggplot(stats, aes(x=n.utterances, y=boundary.noedge.F, colour=language, group=child)) + geom_line() + facet_wrap(~wordseg) + theme_bw()
