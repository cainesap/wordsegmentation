## libraries
if (!require("pacman")) install.packages("pacman")
suppressMessages(library(pacman))
pacman::p_load(ggplot2)


## load data
stats <- read.csv('~/Corpora/CHILDES/segmentation_experiment_stats.csv', as.is=T)
stats$wordseg <- toupper(stats$wordseg)
stats$language <- paste0(toupper(substring(stats$language, 1, 1)), substring(stats$language, 2))


## basic stats
# n.languages
length(unique(stats$language))
# n.corpora
length(unique(stats$corpus))
# n.children
length(unique(stats$child))

## CDS token counts for each lang @ 1000 and 10,000 utterances
print('N.utterances: 1000')
sumTokens <- 0
for (lang in unique(stats$language)) {
  tokenCount <- sum(subset(subset(subset(stats, language==lang), n.utterances==1000), wordseg=='BASELINE')$tokens)
  sumTokens <- sumTokens + tokenCount
  print(paste(lang, tokenCount))
}
print(paste('TOTAL:', sumTokens))

print('N.utterances: 10,000')
sumTokens <- 0
for (lang in unique(stats$language)) {
  tokenCount <- sum(subset(subset(subset(stats, language==lang), n.utterances==10000), wordseg=='BASELINE')$tokens)
  sumTokens <- sumTokens + tokenCount
  print(paste(lang, tokenCount))
}
print(paste('TOTAL:', sumTokens))


## plots of type, token, boundary P R F
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



## CHECK COLUMN NUMBERS


## performance stats for each wordseg model
## for table of results
mods <- unique(stats$wordseg)

algos <- c('UTT_BASELINE', 'RAND_BASELINE', 'UNIT_BASELINE', 'ORACLE', 'TP_FTP', 'TP_BTP', 'TP_MI', 'DIBS', 'PUDDLE')
fCols <- c(17, 20, 23)

## at 1000(0) utterances
for (nutt in c(1000, 10000)) {
  print(paste(nutt, 'utterances'))
  subs <- subset(stats, n.utterances==nutt)

  ## col.means
  for (algo in algos) {
    algo.sub <- subset(subs, wordseg==algo)
    print(paste(algo, 'means'))
    colMeans(algo.sub[,15:26])
    print('standard deviation')
    quantile(unlist(lapply(algo.sub[,15:26], sd)))
  }

  ## pairwise stats tests
  for (c in fCols) {
    print(colnames(stats)[c])
    pvalues <- c()
    for (i in 1:(length(algos)-1)) {
      x.algo <- algos[i]
      x.subs <- subset(subs, wordseg==x.algo)
      y.aglos <- algos[(i+1):length(algos)]
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


langs <- unique(stats$language)
lang.df <- data.frame()
for (lang in langs) {
#  print(lang)
#  subs <- subset(u10k, language==lang)
  subs <- subset(puddle, language==lang)
#  subs <- subset(dibs, language==lang)
  typeF <- mean(subs[,17])
  tokenF <- mean(subs[,20])
  boundary.all.F <- mean(subs[,23])
  lineout <- data.frame(lang, typeF, tokenF, boundary.all.F)
  lang.df <- rbind(lang.df, lineout)
}
#print('PUDDLE')
print('DIBS')
print(lang.df[with(lang.df, order(-tokenF)),])


## regression models
dibs <- subset(stats, wordseg=='DIBS')
#summary(lm(data=dibs, tokenP~prop.owus+TTR+boundary.entropy+fzm.alpha))
summary(lm(data=dibs, tokenP~prop.owus+(TTR*n.utterances)+boundary.entropy+zm.alpha+zm.X2))

puddle <- subset(stats, wordseg=='PUDDLE')
#summary(lm(data=puddle, tokenP~prop.owus+TTR+boundary.entropy+fzm.alpha))
summary(lm(data=puddle, tokenP~prop.owus+(TTR*n.utterances)+boundary.entropy+zm.alpha+zm.X2))
