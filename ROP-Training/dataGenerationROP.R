################################################################################
# Description : Program to automatically generate "apprentissage" files for ROP model training.
# Author : Mathieu Brunner.
################################################################################

# Function for file generation --------------------------------------------

fileGenerationStratified <- function(stratColumn, data, nbVar, nbVarROP, nbTree, simulationRange) {
  "
  Generates ROP-Training samples (.csv files) for specified stratified variable and configuration.
  
  Parameters :
    stratColumn : vector. Column of .csv dataset corresponding to the stratified variable.
    data : dataFrame. Imported .csv dataset without stratColumn.
    nbVar : integer. Number of variables in dataset without the stratified one.
    nbVarROP : integer. Number of selected variables in each tree.
    nbTree : integer. Number of trees in each forest.
    simulationRange : integer. Range of simulation range.
    
  Returns :
    no return.
  "
  # Range of simulation definition.
  infRange <- - (simulationRange %/% 2)
  if ((simulationRange %% 2) == 0) {
    supRange <- (simulationRange %/% 2) - 1
  } else {
    supRange <- (simulationRange %/% 2)
  }
  data[2,3:ncol(data)] <- rep(infRange, nbVar)
  data[3,3:ncol(data)] <- rep(supRange, nbVar)
  
  # Strat column.
  stratColumn[2,] <- infRange
  stratColumn[3,] <- supRange
  
  # "Apprentissage" file creation.
  for (i in 1:nbTree){
    fileName <- paste("apprentissage_", i ,".csv", sep = "")
    if (!(file.exists(fileName))) {
      selectedFeatures <- sample(1:(nbVar-1), nbVarROP-1, replace = F) # Feature selection.
      selectedFeatures <- selectedFeatures + 2
      fileContent <- data[, c(1, 2, selectedFeatures)]
      fileContent <- cbind(fileContent, stratColumn)
      write.csv2(fileContent, fileName, row.names = F, quote = F) # File writing.
    }
  }
}


# Main ---------------------------------------------------------------------

# Set current working directory.
referenceWD <- "C:/Users/FEU49/Desktop/Wisconsin/" # Reference Working Directory.
setwd(referenceWD)


# Data importation.
dataPath <- "C:/Users/FEU49/Desktop/Wisconsin/wisconsin.csv"     # Absolute path towards dataset .csv file.
data <- read.csv2(dataPath)                           # Data importation.

# Constant definition.
nbVar <- ncol(data) - 2   # First two columns : observations id and target.
nbTree <- 100            # Number of trees in the forest.
infR <- 3
supR <- 9
infV <- 3
supV <- 10

# Generating ROP-Training samples for each stratified variable..
for (i in 1:nbVar) {
  stratVar <- paste("a", i, sep = "")
  dir.create(stratVar) # Create new folder for stratified variable.
  setwd(stratVar)
  stratIndex <- which(colnames(data) %in% c(stratVar)) # Index of stratified variable.
  dataStrat <- data[,-stratIndex] # Dataset without stratified variable.
  nbVarStrat <- ncol(dataStrat) - 2 + 1 # +1 because we add the stratified variable in last position.
  stratColumn <- subset(data, select = c(stratVar)) # Column with stratified variable data.
  
  # Generation of ROP-Training samples for each range of simulation range.
  for (simulationRange in infR:supR) {
    rangeFolder <- paste("R", simulationRange,"/",sep="")
    dir.create(rangeFolder) # Create new folder for range of simulation range.
    setwd(rangeFolder)
    
    # Generation of ROP-Training samples for each number of selected variables.
    for (nbVarROP in infV:supV) {
      varFolder <- paste("V", nbVarROP, "/", sep="")
      dir.create(varFolder) # Create new folder for number of selected variables.
      setwd(varFolder)
      fileGenerationStratified(stratColumn, dataStrat, nbVarStrat, nbVarROP, nbTree, simulationRange)
      setwd("..")
    }
    setwd("..")
  }
  setwd("..")
}