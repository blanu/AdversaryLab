data {
  int<lower=1> N; // number of samples
  real<lower=0> samples[N];
}

parameters {
  real theta;
  real sigma;
}

model {
  for(n in 1:(N-1))
    samples[n] ~ normal(theta, sigma);
}
