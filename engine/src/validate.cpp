#include <algorithm>
#include <array>
#include <iostream>
#include <fstream>
#include <random>
#include <stdexcept>
#include <vector>
#include "solver/solver.h"
struct Plain {
 int a[9][9]{};int h[9]{};int n=0;
 bool won(int who) const {for(int c=0;c<9;c++)for(int r=0;r<9;r++)for(auto [dc,dr]:std::array<std::pair<int,int>,4>{{{1,0},{0,1},{1,1},{1,-1}}}){bool ok=true;for(int k=0;k<4;k++){int x=c+k*dc,y=r+k*dr;if(x<0||x>=9||y<0||y>=9||a[x][y]!=who){ok=false;break;}}if(ok)return true;}return false;}
 void move(int c){a[c][h[c]++]=1+n%2;n++;}void undo(int c){a[c][--h[c]]=0;n--;}
 int exact(){int me=1+n%2;if(won(3-me))return -1;if(n==81)return 0;int best=-1;for(int c=0;c<9;c++)if(h[c]<9){move(c);int v=-exact();undo(c);best=std::max(best,v);if(best==1)break;}return best;}
};
int main(){std::mt19937 rng(20261105);long states=0,threats=0;int endgames=0;Solver solver;std::ofstream fixtures("fixtures-9x9.jsonl");int values[3]{};int oracle_proofs=0,oracle_wins=0;
 for(int trial=0;trial<5000;trial++){
  Plain b;Position p;std::string seq;
  while(b.n<81){
   int me=1+b.n%2;
   if(p.has_player_won()!=b.won(me)||p.has_opponent_won()!=b.won(3-me))throw std::runtime_error("win disagreement");
   if(!p.are_dead_stones_valid())throw std::runtime_error("dead-stone disagreement");
   for(int c=0;c<9;c++)if(b.h[c]<9){int row=b.h[c];b.move(c);bool w=b.won(me);b.undo(c);board bit=board(1)<<(10*c+row);bool t=bool(p.find_player_threats()&bit);if(w!=t)throw std::runtime_error("threat disagreement");threats++;}
   states++;
   if(b.n>=73&&endgames<100){int ref=b.exact();int bound=p.pairing_upper_bound();if(bound!=Position::MAX_SCORE){oracle_proofs++;if(bound==-1)oracle_wins++;if(ref>bound)throw std::runtime_error("unsound pairing bound");}int actual=solver.solve(p);if(ref!=actual)throw std::runtime_error("exact endgame disagreement");values[ref+1]++;fixtures<<"{\"moves\":\""<<seq<<"\",\"side_to_move_value\":"<<ref<<"}\n";endgames++;}
   std::vector<int> safe,legal;
   for(int c=0;c<9;c++)if(b.h[c]<9){legal.push_back(c);b.move(c);board old=p.move(c);if(!b.won(me)&&!p.wins_this_move(p.find_player_threats()))safe.push_back(c);p.unmove(old);b.undo(c);}
   if(safe.empty())break;
   int c=safe[rng()%safe.size()];b.move(c);p.move(c);seq+=char('1'+c);
  }
 }
 std::cout<<"PASS independent_array_states="<<states<<" immediate_threat_checks="<<threats<<" independent_exact_endgames="<<endgames<<" seed=20261105 losses="<<values[0]<<" draws="<<values[1]<<" wins="<<values[2]<<" pairing_bounds="<<oracle_proofs<<" pairing_forced_losses="<<oracle_wins<<"\n";
 return endgames==100?0:4;
}
