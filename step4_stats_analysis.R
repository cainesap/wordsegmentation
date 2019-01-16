## libraries
if (!require("pacman")) install.packages("pacman")
suppressMessages(library(pacman))
pacman::p_load(ggplot2, reshape2, lme4, MuMIn, jtools)


## initial stats from step1
stats0 <- read.delim('~/Corpora/CHILDES/corpus_statistics.txt', as.is=T)

## basic stats used throughout
# n.languages
length(unique(stats0$language))
# n.corpora
length(unique(paste(stats0$language, stats0$corpuscollection)))
# n.children
length(unique(paste(stats0$corpuscollection, stats0$child)))  # should match nrow(stats0)


## per language stats: Table 1
langs <- unique(stats0$language)
langs <- langs[order(langs)]
totalPartis <- 0
for (lang in langs) {
 subs <- subset(stats0, language==lang)
 print(paste("====", lang))
 print(paste('N.collect:', length(unique(subs$corpuscollection))))
 print(paste('N.corpora:', length(unique(subs$child))))
 nPartis <- sum(subs$n.participants)
 print(paste('N.partic:', nPartis))
 totalPartis <- totalPartis + nPartis
}
print(paste('Total participants:', totalPartis))  # total n.participants


## secondary stats from step3 wordseg experiments
stats <- read.csv('~/Corpora/CHILDES/segmentation_experiment_stats.csv', as.is=T)
stats$wordseg <- toupper(stats$wordseg)
stats$language <- paste0(toupper(substring(stats$language, 1, 1)), substring(stats$language, 2))


# token counts for each lang: Table 1 cont'd
sumTokens <- 0
for (lang in langs) {
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
    print(round(colMeans(algo.sub[,ttbcols]), 3))
  }
}

## pairwise stats tests between each model for each F-measure
fCols <- c(21, 24, 27)
for (nutt in c(1000, 10000)) {
  subs <- subset(stats, n.utterances==nutt)
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

# how much variation? (used in text)
print(lapply(lang.df[,fCols], range))
print(lapply(lang.df[,fCols], sd))

# F measures only (Table 3)
print(round(lang.df[,fCols], 3))



## FIGURES
## plots of type, token, boundary P R F
algos <- unique(stats$wordseg)
stats$corpusID <- paste0(stats$language, '_', stats$corpus, '_', stats$child)

# boxplot of per model F-measures (Figure 1)
subs <- subset(stats, n.utterances==10000)
submelt <- melt(subs, id.var=c('corpusID', 'wordseg'), measure.var=c('typeF', 'tokenF', 'boundary.all.F'))
submelt$wordseg <- factor(submelt$wordseg, levels=algos)
ggplot(submelt, aes(x=variable, y=value)) + geom_boxplot(outlier.alpha=1/4) + facet_wrap(~wordseg) +
  theme_bw() + theme(text=element_text(family="Times")) + scale_x_discrete('') + scale_y_continuous('', breaks=seq(0, 1, .1)) 

# boxplots of token F at each 1000 utterance increment (Figure 2)
statsmelt <- melt(stats, id.var=c('corpusID', 'wordseg', 'n.utterances'), measure.var='tokenF')
statsmelt$wordseg <- factor(statsmelt$wordseg, levels=algos)
ggplot(statsmelt, aes(x=n.utterances, y=value, group=n.utterances)) + geom_boxplot(outlier.alpha=1/4) + facet_wrap(~wordseg) +
  theme_bw() + theme(text=element_text(family="Times")) + scale_x_continuous('Corpus size (utterances)') + scale_y_continuous('', breaks=seq(0, 1, .1)) 

# boxplots of language properties: use puddle (one model only) to avoid repetition of datapoints (Figure 3)
puddle <- subset(stats, wordseg=='PUDDLE')
statsmelt <- melt(puddle, id.var=c('corpusID', 'n.utterances', 'language'),
  measure.var=c('types', 'TTR', 'prop.owus', 'boundary.entropy', 'zm.alpha', 'mean.phones.per.word'))
# relabel for plot
levels(statsmelt$variable) <- c('types', 'type-token ratio', 'one-word utterance prop.', 'H(boundary diphones)', 'Zipf-Mandelbrot (α)', 'phoneme/word (μ)')
ggplot(statsmelt, aes(x=n.utterances, y=value, group=n.utterances)) + geom_boxplot(outlier.alpha=1/4) + facet_wrap(~variable, scales='free') +
  theme_bw() + theme(text=element_text(family="Times")) + scale_x_continuous('Corpus size (utterances)', breaks=seq(0,10000,2000)) + scale_y_continuous('') 



## REGRESSION models for PUDDLE token F
range01 <- function(x){(x-min(x))/(max(x)-min(x))}  # scale between 0 and 1
puddle <- subset(stats, wordseg=='PUDDLE')
puddle$corpusID <- paste0(puddle$language, '_', puddle$corpus, '_', puddle$child)
puddle$corpusID <- as.factor(puddle$corpusID)
puddle$boundary.entropy <- range01(puddle$boundary.entropy)
puddle$zm.X2 <- range01(puddle$zm.X2)
puddle$mean.phones.per.word <- range01(puddle$mean.phones.per.word)

# add families
langs <- unique(stats0$language)
langs <- langs[order(langs)]
fams <- c('Unknown', 'Sinitic', 'Balto-Slavic', 'Germanic', 'Germanic',
  'Germanic', 'Germanic', 'Finnic', 'Indo-Iranian', 'Italic',
  'Germanic', 'Graeco-Phrygian', 'Uralic', 'Germanic', 'Malayo-Polynesian',
  'Celtic', 'Italic', 'Japanesic', 'Koreanic', 'Sinitic', 
  'Germanic', 'Italic', 'Italic', 'Italic', 'Balto-Slavic',
  'Italic', 'Germanic', 'Common Turkic'
)
puddle$family <- ''
for (r in 1:nrow(puddle)) {
  lg <- puddle$language[r]
  fam <- fams[which(langs==lg)]
  puddle$family[r] <- fam
}
puddle$family <- as.factor(puddle$family)
puddle$isGermanic <- ifelse(puddle$family=='Germanic', TRUE, FALSE)
puddle$isItalic <- ifelse(puddle$family=='Italic', TRUE, FALSE)

# linear model 1: 5 properties
mod1 <- lm(data=puddle, tokenF ~ prop.owus+TTR+boundary.entropy+zm.alpha+zm.X2+mean.phones.per.word)
r.squaredGLMM(mod1)
AIC(mod1)

mod2 <- lm(data=puddle, tokenF ~ prop.owus+(TTR*n.utterances)+boundary.entropy+zm.alpha+zm.X2+mean.phones.per.word)
r.squaredGLMM(mod2)
AIC(mod2)

mod3 <- lm(data=puddle, tokenF ~ prop.owus+(TTR*n.utterances)+boundary.entropy+zm.alpha+zm.X2+mean.phones.per.word+isGermanic)
r.squaredGLMM(mod3)
AIC(mod3)

mod4 <- lm(data=puddle, tokenF ~ prop.owus+(TTR*n.utterances)+boundary.entropy+zm.alpha+zm.X2+mean.phones.per.word+isGermanic+isItalic)
r.squaredGLMM(mod4)
AIC(mod4)

mod5 <- lmer(data=puddle, tokenF ~ prop.owus+(TTR*n.utterances)+boundary.entropy+zm.alpha+zm.X2+mean.phones.per.word+isGermanic+isItalic+(1|corpusID))
r.squaredGLMM(mod5)
AIC(mod5)
summ(mod5, scale=T)  # from jtools

# pairwise comparisons: pass lmer object first
anova(mod5, mod4)
anova(mod5, mod3)
anova(mod5, mod2)
anova(mod5, mod1)
