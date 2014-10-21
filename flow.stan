# Number of packets sent per second as a Poisson distribution

data {
  int<lower=1> N; // number of samples
  int<lower=0> samples[N];
}

parameters {
  real lambda;
}

model {
  lambda ~ gamma(1, 1);

  for(n in 1:(N-1))
    samples[n] ~ poisson(lambda);
}
