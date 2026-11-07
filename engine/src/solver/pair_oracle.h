#ifndef PAIR_ORACLE_H
#define PAIR_ORACLE_H
#include <array>
#include <bit>
#include <cstdint>
#include "types.h"
// Sufficient theorem: the opponent can reply by completing legal pairs.
// If all our winning lines are blocked, V <= 0. If their guaranteed cells
// also contain four, V = -1. Unknown is MAX_SCORE (never a heuristic zero).
inline int pair_upper_bound(board us,board them,int moves_played) noexcept {
 if(((BOARD_WIDTH*BOARD_HEIGHT-moves_played)&1)!=0)return Position::MAX_SCORE;
 constexpr int W=BOARD_WIDTH,H=BOARD_HEIGHT,S=H+1;
 constexpr board bottom=[](){board x=0;for(int c=0;c<W;c++)x|=board(1)<<(S*c);return x;}();
 constexpr board valid=bottom*((board(1)<<H)-1);
 constexpr board upper_rows=[](){board x=0;for(int c=0;c<W;c++)for(int r=H-1;r>=0;r-=2)x|=board(1)<<(S*c+r);return x;}();
 board occupied=us|them,next=(occupied+bottom)&valid;
 board guaranteed=them|(upper_rows&~occupied&~next);
 auto won=[](board b){for(int s:{1,H,H+1,H+2}){board q=b&(b>>s);if(q&(q>>(2*s)))return true;}return false;};
 struct Groups {std::array<board,512> g{};int n=0;Groups(){for(int c=0;c<W;c++)for(int r=0;r<H;r++)for(auto d:std::array<std::pair<int,int>,4>{{{1,0},{0,1},{1,1},{1,-1}}}){int x=c+3*d.first,y=r+3*d.second;if(x<0||x>=W||y<0||y>=H)continue;board mask=0;for(int k=0;k<4;k++)mask|=board(1)<<((c+k*d.first)*S+r+k*d.second);g[n++]=mask;}}};
 static const Groups groups;
 std::array<board,W> odd{};int n=0;
 for(int c=0;c<W;c++){board b=next&(((board(1)<<H)-1)<<(S*c));if(b&upper_rows)odd[n++]=b;}
 if(n&1)return Position::MAX_SCORE;
 // Each constraint is a bit set of odd-height columns. Some pair inside
 // this set must be selected. Already occupied opponent cells and guaranteed
 // vertical upper cells block lines without any matching constraint.
 std::array<unsigned,512> required{};int nr=0;
 for(int j=0;j<groups.n;j++){
  board g=groups.g[j];if(g&guaranteed)continue;
  unsigned mask=0;for(int i=0;i<n;i++)if(g&odd[i])mask|=1u<<i;
  if(std::popcount(mask)<2)return Position::MAX_SCORE;
  required[nr++]=mask;
 }
 auto cover=[&](auto&&self,unsigned available,const std::array<unsigned,512>&req,int count)->bool{
  if(!count)return true;
  int best=-1,best_n=100;
  for(int i=0;i<count;i++){int size=std::popcount(req[i]&available);if(size<2)return false;if(size<best_n){best=i;best_n=size;}}
  unsigned choices=req[best]&available;
  for(unsigned a=choices;a;a&=a-1){unsigned x=a&-a;
   for(unsigned b=choices&~((x<<1)-1);b;b&=b-1){unsigned y=b&-b,pair=x|y;std::array<unsigned,512> next_req{};int nc=0;
    for(int j=0;j<count;j++)if((req[j]&pair)!=pair)next_req[nc++]=req[j];
    if(self(self,available&~pair,next_req,nc))return true;
   }
  }
  return false;
 };
 if(!cover(cover,(1u<<n)-1,required,nr))return Position::MAX_SCORE;
 return won(guaranteed)?-1:0;
}
#endif
