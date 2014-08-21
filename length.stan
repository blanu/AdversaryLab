data {
  int samples;
  real packetLength[samples];
}

parameters {
  real theta1;
  real sigma1;
}

transformed parameters {
}

model {
  packetLength ~ normal(theta1, sigma1);
}
