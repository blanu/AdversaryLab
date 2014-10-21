data {
  int<lower=1> N; // number of samples
  real<lower=0> samples[N];
}

parameters {
  real lambda;
}

model {
  lambda ~ gamma(1, 1);

  for(n in 1:(N-1))
    samples[n] ~ exponential(lambda);
}
