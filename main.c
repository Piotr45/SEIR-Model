#include <stdio.h>
#include <float.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>

#define paramsLength 6


int survivors=10;
int numberOfSimulations=100,totalPopulation=10000, startingNumberOfSick=1, cycles;
int simulationTime = 365;
int simulationStep =5;
int iterations =100;//można zmienić
double scatter = 0.20;//można zmienić
int probingPeriod = 10;
double* maxParams;
double* minParams;
double** perfect;
bool firstTime = true;
double ***Simulations;
double **params;
double *scores;

void setPerfect();
void write2(double ***Simulation,bool t);
void scoredSeirImplementation(double ***Simulation, double **parameters, double *score);
void write(double*** Simulation);
double randomDouble(double max, double min);
void semiRandValues(double* parameters);
void seirImplementation(double** Simulation,const double *parameters);
void MuteateAndCross(double **Params);
void setParams();
void trueWrite(FILE * fp, double ***Simulation);

bool cmp(const double* a, const double* b){
    return *a<*b;
}
enum modes{
    Calculator,
    GeneticAlgorithm
};
/**
 * funkcja wmiare ok dla x < sqrt(survivous)
 * @param score tablica wyników
 * @param survivous ilość najlepszych indeksów
 * @return tablica najlepszych ineksów
 */
int* bestXSimulations(double* score, bool(*compare)(const double *a, const double *b));

void calculatorRead(char **argv);

void mallocThings2();

void geneticRead(char **argv);

/**
 *  Kolejne argumenty:
 *  1 - tryb operacji:
 *      0 zwykły kalkulator seir
 *      1 heurystyka
 *
 * @param argc
 * @param argv
 * @return
 */
int main(int argc, char **argv) {
    enum modes mode =atoi(argv[1]);
    srand(time(0));
    cycles=simulationTime/simulationStep;
    switch (mode) {
        case Calculator:
            numberOfSimulations=1;
            Simulations = (double***)malloc(numberOfSimulations*sizeof(double**));
            params= (double**)malloc(numberOfSimulations*sizeof(double*));
            params[0]=(double*)malloc(6*sizeof(double));
            calculatorRead(argv);
            Simulations[0]=(double**)malloc(4*sizeof(double*));
            for(int j =0;j<4;++j){
                Simulations[0][j]=(double*)malloc(cycles*sizeof(double));
            }

            seirImplementation(Simulations[0],params[0]);
            write(Simulations);
            free(Simulations);
            free(params);
            break;
        case GeneticAlgorithm:
            maxParams = (double*)malloc(paramsLength *sizeof(double));
            minParams = (double*)malloc(paramsLength *sizeof(double));
            geneticRead(argv);
            setParams();
            mallocThings2();
            setPerfect();
            for (int j = 0; j < iterations; ++j) {
                scoredSeirImplementation(Simulations,params,scores);
                int* tmp = bestXSimulations(scores, cmp);
                double*** tmpSimulations = (double ***)malloc(survivors * sizeof(double **));
                double** tmpParams= (double**)malloc(survivors * sizeof(double*));
                for (int i = 0; i < survivors; ++i) {
                    tmpSimulations[i]=Simulations[tmp[i]];
                    tmpParams[i]=params[tmp[i]];
                }
                for (int i = 0; i < survivors; ++i) {
                    Simulations[0]= tmpSimulations[i];
                    params[tmp[i]]=tmpParams[i];
                }
                MuteateAndCross(params);
                if(j%probingPeriod == 0 && j != 0 ){
                    write2(Simulations,false);
                    }
                free(tmpSimulations);
                free(tmpParams);
            }
            scoredSeirImplementation(Simulations,params,scores);
            int* tmp = bestXSimulations(scores, cmp);
            double*** tmpSimulations = (double ***)malloc(survivors * sizeof(double **));
            double** tmpParams= (double**)malloc(survivors * sizeof(double*));
            for (int i = 0; i < survivors; ++i) {
                tmpSimulations[i]=Simulations[tmp[i]];
                tmpParams[i]=params[tmp[i]];
            }
            for (int i = 0; i < survivors; ++i) {
                Simulations[0]= tmpSimulations[i];
                params[tmp[i]]=tmpParams[i];
            }
            free(tmpSimulations);
            free(tmpParams);
            write2(Simulations,true);
            free(Simulations);
            free(params);
            break;
    }
    return 0;
}

void geneticRead(char **argv) {
    scatter = atof(argv[2]);
    iterations = atoi(argv[3]);
    probingPeriod = atoi(argv[4]);
}

void mallocThings2() {
    Simulations = (double***)malloc(numberOfSimulations*sizeof(double**));
    params= (double**)malloc(numberOfSimulations*sizeof(double*));
    scores=(double*)malloc(numberOfSimulations*sizeof(double));
    #pragma omp parallel for
    for(int i=0; i <numberOfSimulations;++i){
        Simulations[i]=(double**)malloc(4*sizeof(double*));
        for(int j =0;j<4;++j){
            Simulations[i][j]=(double*)malloc(cycles*sizeof(double));
        }
        params[i]=(double*)malloc(6*sizeof(double));
        semiRandValues(params[i]);
    }

}

void calculatorRead(char **argv) {
    simulationTime = atoi(argv[2]);
    cycles = simulationTime / simulationStep;
    params[0][4]= atof(argv[3]);
    params[0][5] = atof(argv[4]);
    for (int i = 0; i < paramsLength-2; ++i) {
        params[0][i]=atof(argv[i+5]);
        printf("%f ", params[0][i]);
    }
}

void setParams(){
    maxParams[0]= 0.2000*(1- scatter);
    maxParams[1]= 0.31429*(1- scatter);
    maxParams[2]= 0.14286*(1- scatter);
    maxParams[3]= 0.00549*(1- scatter);
    maxParams[4]= 2.2*(1- scatter);
    maxParams[5]= 1*(1- scatter);
    minParams[0]= 0.2000*(1+ scatter);
    minParams[1]= 0.31429*(1+ scatter);
    minParams[2]= 0.14286*(1+ scatter);
    minParams[3]= 0.00549*(1+ scatter);
    minParams[4]= 2.2*(1+ scatter);
    minParams[5]= 1*(1+ scatter);
}

void mutate(double *target, double *source) {
    target = source;
    int point = rand() % paramsLength;
    target[point]= randomDouble(maxParams[point], minParams[point]);
}

void cross(double * target, const double *source1, const double *source2) {
    int point = rand() % paramsLength;
    for (int i = 0; i < point; ++i) {
        target[i]=source1[i];
    }
    for (int i = point; i < paramsLength; ++i) {
        target[i]=source2[i];
    }
}

void MuteateAndCross(double **Params) {
    int rand1,rand2;
    for (int i = survivors; i < numberOfSimulations; ++i) {

        rand1 = rand() % 2;
        if(rand1 == 0){
            rand1 = rand() % survivors;
            mutate(Params[i],Params[rand1]);
        }else{
            rand1 = rand() % survivors;
            rand2 = rand() % survivors;
            if(rand1==rand2){
                rand2= (rand2+1) % survivors;
            }
            cross(Params[i],Params[rand1],Params[rand2]);
        }
    }
}

void scoredSeirImplementation(double ***Simulation, double **parameters, double *score) {
#pragma omp parallel for
    for(int id=0 ; id< numberOfSimulations;++id){
        double alpha = parameters[id][0];
        double beta = parameters[id][1];
        double m_gamma = parameters[id][2];
        double sigma = parameters[id][3];
        double basicReproductionNumber = parameters[id][4];
        double mixingParameter = parameters[id][5];
        double S=totalPopulation-startingNumberOfSick,
                E = 0,
                I = startingNumberOfSick,
                R = 0;
        Simulation[id][0][0]=S;
        Simulation[id][1][0]=E;
        Simulation[id][2][0]=I;
        Simulation[id][3][0]=R;
        for(int i = 1 ;i < cycles;++i){
            S += (-beta * I * pow((S / totalPopulation), mixingParameter) + sigma * R) * simulationStep;
            Simulation[id][0][i] = S;
            score[id]+=fabs(perfect[0][i] - Simulation[id][0][i]);
            E += (beta * I * pow((S / totalPopulation), mixingParameter) - alpha * E) * simulationStep;
            Simulation[id][1][i] = E;
            score[id]+=fabs(perfect[1][i] - Simulation[id][1][i]);
            I += (alpha * E - m_gamma * I) * simulationStep;
            Simulation[id][2][i] = I;
            score[id]+=fabs(perfect[2][i] - Simulation[id][2][i]);
            R += (m_gamma * I - sigma * R) * simulationStep;
            Simulation[id][3][i] = R;
            score[id]+=fabs(perfect[3][i] - Simulation[id][3][i]);
            beta = basicReproductionNumber * m_gamma;
        }
    }
}

void write(double ***Simulation) {
    FILE * fp;
    fp = fopen("output.txt","w");
    fprintf(fp,"%d\t%d \n",numberOfSimulations,cycles);
    for(int i =0; i< numberOfSimulations; ++i){
        fprintf(fp,"%d\n",i);
        for(int j=0 ;j<paramsLength-1;++j){
            fprintf(fp, "%f\t", params[i][j]);
        }
        fprintf(fp, "%f\n", params[i][paramsLength - 1]);
        for(int j=0 ; j<4 ; ++j){
            for (int k =0 ;k< cycles-1; ++k ){
                fprintf(fp,"%f\t",Simulation[i][j][k]);
            }
            fprintf(fp,"%f\n",Simulation[i][j][cycles-1]);
        }
        fprintf(fp,"\n");
    }
    fclose(fp);
}

double randomDouble(double max, double min) {
    double range = (max - min);
    double div = RAND_MAX / range;
    return min + (rand() / div);
}

void semiRandValues(double *parameters) {
    for (int j = 0; j < paramsLength; ++j) {
        parameters[j]=randomDouble(maxParams[j],minParams[j]);
    }
}

int *bestXSimulations(double *score, bool (*compare)(const double *, const double *)) {
    int* out;
    out = (int*)malloc(survivors * sizeof(int));
    double compared;
    for(int i=0 ; i < survivors ; ++i){
        compared = score[0];
        out[i]=0;
        for (int j = i+1; j < numberOfSimulations; ++j) {
            if(compare(&score[j],&compared)){
                compared= score[j];
                out[i]=j;
            }
        }
        score[out[i]] = DBL_MAX;
    }
    return out;
}

int offset=0;
void trueWrite(FILE *fp, double ***Simulation) {
        fprintf(fp,"%d\n",offset++);
        for(int j=0 ;j<paramsLength-1;++j)
            fprintf(fp,"%f\t",params[0][j]);
        fprintf(fp,"%f\n",params[0][paramsLength-1]);
        for(int j=0 ; j<4 ; ++j){
            for (int k =0 ;k< cycles-1; ++k ){
                fprintf(fp,"%f\t",Simulation[0][j][k]);
            }
            fprintf(fp,"%f\n",Simulation[0][j][cycles-1]);
        }
        fprintf(fp,"\n");
}

FILE *ftp;
void write2(double ***Simulation, bool t) {
    if (firstTime) {
        ftp = fopen("output.txt", "w");
        fprintf(ftp, "%d\t%d \n", iterations/probingPeriod, cycles);
        firstTime = false;
    }
    trueWrite(ftp, Simulation);
    if (t) {
        fclose(ftp);
    }
}

void setPerfect() {
    perfect=(double**)malloc(4*sizeof(double*));
    for (int i = 0; i < 4; ++i) {
        perfect[i] = (double*)malloc(cycles*sizeof(double));
    }
    FILE * fp;
    fp = fopen("perfect.txt","r");
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < cycles; ++j) {
            fscanf(fp,"%f", &perfect[i][j]);
        }
    }
}

void seirImplementation(double **Simulation, const double *parameters) {
        double alpha = parameters[0];
        double beta = parameters[1];
        double m_gamma = parameters[2];
        double sigma = parameters[3];
        double basicReproductionNumber = parameters[4];
        double mixingParameter = parameters[5];
        double S=totalPopulation-startingNumberOfSick,
                E = 0,
                I = startingNumberOfSick,
                R = 0;
        Simulation[0][0]=S;
        Simulation[1][0]=E;
        Simulation[2][0]=I;
        Simulation[3][0]=R;
        for(int i = 1 ;i < cycles;++i){
            S += (-beta * I * pow((S / totalPopulation), mixingParameter) + sigma * R) * simulationStep;
            Simulation[0][i] = S;
            E += (beta * I * pow((S / totalPopulation), mixingParameter) - alpha * E) * simulationStep;
            Simulation[1][i] = E;
            I += (alpha * E - m_gamma * I) * simulationStep;
            Simulation[2][i] = I;
            R += (m_gamma * I - sigma * R) * simulationStep;
            Simulation[3][i] = R;
            beta = basicReproductionNumber * m_gamma;
        }

}



