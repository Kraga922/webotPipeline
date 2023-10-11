import torch

#rew_file = '/project/nscore/webots/webots-data/ppl/b32-lr0.01-clip0.2-epi500-epo4/rewards.pth'
rew_file = '/Users/krishivagarwal/Downloads/rewards.pth'
obj = torch.load(rew_file)
all_rewards = obj['all_rewards']





# print (type(all_rewards))
mean_rewards = all_rewards.mean(dim=1)
print (f"Reward for episode 0: {mean_rewards[0]} ")
for i in range(0, 501, 25):
    print (f"Reward for episode {i}: {mean_rewards[i-1]} ")

dist_from_mean = torch.abs(all_rewards - mean_rewards.unsqueeze(-1))
closest_to_mean = torch.argmin(dist_from_mean, dim=1)
#best_design_per_ep = torch.median(all_rewards, dim=1)

#print (best_design_per_ep)
print(closest_to_mean[0])
# print(best_design_per_ep[1])

for i in range(0, 501, 25):
    print (f" {i}: {closest_to_mean[i-1]}, ")
