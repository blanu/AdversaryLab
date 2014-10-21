# Given a position 0-1440 and a previous byte 0-255 and a next byte 0-255, count the number of occurrences

data {
  int<lower=1> L; // 1440
  int<lower=1> B; // 256

  int<lower=0> counts[L, B, B];
}

parameters {
  simplex[B]<lower=0> alpha[L,B];
  simplex[B]<lower=0> theta[L,B];
}

model {
  for(l in 1:(L-1))
    for(b in 1:(B-1))
      for(b2 in 1:(B-1))
        alpha[l,b,b2] ~ normal(1,1);

  for(l in 1:(L-1))
    for(b in 1:(B-1))
      theta[l,b] ~ dirichlet(alpha[l,b]);

  for(l in 1:(L-1))
    for(b in 1:(B-1))
      counts[l,b] ~ multinomial(theta[l,b]);
}
