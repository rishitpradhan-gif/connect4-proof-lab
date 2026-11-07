#define main horizon_main
#include "horizon.cpp"
#undef main
#include <random>
#include <fstream>
#include <stdexcept>
struct Plain {
 int a[9][9]{};int h[9]{};int n=0;
 bool won(int who) const {for(int c=0;c<9;c++)for(int r=0;r<9;r++)for(auto [dc,dr]:std::array<std::pair<int,int>,4>{{{1,0},{0,1},{1,1},{1,-1}}}){bool ok=true;for(int k=0;k<4;k++){int x=c+k*dc,y=r+k*dr;if(x<0||x>=9||y<0||y>=9||a[x][y]!=who){ok=false;break;}}if(ok)return true;}return false;}
 void move(int c){a[c][h[c]++]=1+n%2;n++;}void undo(int c){a[c][--h[c]]=0;n--;}
 int exact(){int me=1+n%2;if(won(3-me))return -1;if(n==81)return 0;int best=-1;for(int c=0;c<9;c++)if(h[c]<9){move(c);int v=-exact();undo(c);best=std::max(best,v);if(best==1)break;}return best;}
};

int reference(Plain &b,int d){int me=1+b.n%2;if(b.won(3-me))return -1;if(!d||b.n==81)return 0;int v=-1;for(int c=0;c<9;c++)if(b.h[c]<9){b.move(c);int x=-reference(b,d-1);b.undo(c);v=std::max(v,x);if(v==1)break;}return v;}
int main(){std::mt19937 rng(34987);int tests=0;budget=3600;for(int t=0;t<250;t++){Plain b;U a=0,o=0,m=0;int target=rng()%73;for(int j=0;j<target;j++){std::vector<int> safe;for(int c=0;c<9;c++)if(b.h[c]<9){int me=1+b.n%2;b.move(c);if(!b.won(me))safe.push_back(c);b.undo(c);}if(safe.empty())break;int c=safe[rng()%safe.size()];U bit=U(1)<<(10*c+b.h[c]);b.move(c);U old=a;a=o;o=old|bit;m|=bit;}for(int d=1;d<=4;d++){int expected=reference(b,d);int actual=search(a,o,m,d,-1,1);if(actual!=expected)throw std::runtime_error("horizon mismatch");tests++;}}std::ifstream fixtures("fixtures-9x9.jsonl");std::string line;int endgames=0;
while(std::getline(fixtures,line)){auto begin=line.find(":\"")+2;auto end=line.find('"',begin);std::string history=line.substr(begin,end-begin);auto valuepos=line.find("side_to_move_value\"");int expected=std::stoi(line.substr(line.find(':',valuepos)+1));U a=0,o=0,mask=0;int heights[9]{};for(char ch:history){int c=ch-'1';U bit=U(1)<<(10*c+heights[c]++);U old=a;a=o;o=old|bit;mask|=bit;}int actual=search(a,o,mask,81-history.size(),-1,1);if(actual!=expected)throw std::runtime_error("full-horizon endgame mismatch");endgames++;}
if(endgames!=100)throw std::runtime_error("missing endgame fixtures");
std::cout<<"PASS independent_horizon_tests="<<tests<<" independent_full_depth_endgames="<<endgames<<" seed=34987 depths=1..4\n";}
