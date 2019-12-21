# coding=utf8
import urllib


def main():
    pp = "status=active&advertiser=5df8c50410768e44b351cc66&start_at=2019-12-20+21%3A35%3A58&trafficback_url=&caps=%5B%7B%27period%27%3A+%27day%27%2C+%27value%27%3A+500%2C+%27affiliates%27%3A+%5B%5D%2C+%27goals%27%3A+%7B%7D%2C+%27type%27%3A+%27conversions%27%2C+%27goal_type%27%3A+%27all%27%2C+%27affiliate_type%27%3A+%27all%27%7D%5D&is_top=0&is_cpi=0&logo=http%3A%2F%2Fcdn-adn.smardroid.com%2Fcdn-adn%2Fdmp%2F18%2F01%2F17%2F18%2F23%2F5a5f241f4177b.jpg&title=MB%7C%7C%7CUnibet_Sportsbook_UK_iOS_CPR+%28appname%29%7CCPA%7CM2320&url=https%3A%2F%2Ftapcrane.hotrk0.com%2Foffer%3Foffer_id%3D373014%26aff_id%3D5074%26aff_sub%3D%5Bclick_id%5D%26aff_pub%3D%5Bsource%5D%26idfa%3D%5Bidfa%5D&url_preview=https%3A%2F%2Fapps.apple.com%2Fapp%2Funibet-live-sports-betting%2Fid463335337&privacy=public&stopDate=2020-11-24+11%3A13%3A21&payments=%5B%7B%27revenue%27%3A+45.0%2C+%27currency%27%3A+%27USD%27%2C+%27total%27%3A+45.0%2C+%27goal%27%3A+1%2C+%27fixed%27%3A+%27fixed%27%7D%5D"
    ppp = urllib.unquote(pp)
    print(ppp)


if __name__ == '__main__':
    main()