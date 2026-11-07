// Independent finite-horizon exact minimax. Zero means unresolved at the horizon.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <vector>
using U=__uint128_t;
const U bottom=[](){U b=0;for(int c=0;c<9;c++)b|=U(1)<<(10*c);return b;}();
const U valid=bottom*511;
U winning(U p){U r=0;for(int s:{1,9,10,11}){r|=(p<<s)&(p<<(2*s))&(p<<(3*s));r|=(p>>s)&(p>>(2*s))&(p>>(3*s));r|=(p<<s)&(p>>s)&(p>>(2*s));r|=(p<<(2*s))&(p<<s)&(p>>s);}return r&valid;}
int pop(U b){return __builtin_popcountll((uint64_t)b)+__builtin_popcountll((uint64_t)(b>>64));}
U mirror(U k){U r=0;for(int c=0;c<9;c++)r|=((k>>(10*c))&1023)<<(10*(8-c));return r;}
struct E{U key=0;int8_t depth=-1,score=0,flag=0,move=4;};
std::vector<E> tt(1<<23);uint64_t nodes=0;auto started=std::chrono::steady_clock::now();int budget=480;
int search(U me,U other,U mask,int depth,int alpha,int beta){
 if((++nodes&262143)==0&&std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count()>budget)throw 1;
 U moves=(mask+bottom)&valid;if(!moves||!depth)return 0;
 U mine=winning(me);if(moves&mine)return 1;
 if(depth==1)return 0;
 U theirs=winning(other),forced=moves&theirs;
 if(forced&&(forced&(forced-1)))return -1;
 if(forced)moves=forced;
 moves&=~(theirs>>1);if(!moves)return -1;
 U k=me+mask+bottom,mir=mirror(k);bool reflected=mir<k;k=std::min(k,mir);
 uint64_t mixed=uint64_t(k)^uint64_t(k>>64)*0x9e3779b97f4a7c15ULL;
 mixed^=mixed>>30;mixed*=0xbf58476d1ce4e5b9ULL;mixed^=mixed>>27;mixed*=0x94d049bb133111ebULL;mixed^=mixed>>31;
 size_t idx=mixed&(tt.size()-1);
 E old=tt[idx];int orig=alpha,preferred=4;
 if(old.key==k){preferred=reflected?8-old.move:old.move;if(old.depth==depth){if(old.flag==0)return old.score;if(old.flag==1)alpha=std::max(alpha,int(old.score));else beta=std::min(beta,int(old.score));if(alpha>=beta)return old.score;}}
 struct M{U b;int c,s;};std::array<M,9> choices;int n=0;
 for(int c=0;c<9;c++){U b=moves&(U(511)<<(10*c));if(b)choices[n++]={b,c,10*pop(winning(me|b)&~mask)+(c==preferred?8:0)+4-std::abs(c-4)};}
 std::sort(choices.begin(),choices.begin()+n,[](M a,M b){return a.s>b.s;});
 int best=-1,bestc=choices[0].c;
 for(int i=0;i<n;i++){auto m=choices[i];int v=-search(other,me|m.b,mask|m.b,depth-1,-beta,-alpha);if(v>best){best=v;bestc=m.c;}alpha=std::max(alpha,v);if(alpha>=beta)break;}
 tt[idx]={k,int8_t(depth),int8_t(best),int8_t(best<=orig?2:best>=beta?1:0),int8_t(reflected?8-bestc:bestc)};
 return best;
}
int main(int argc,char**argv){if(argc>1)budget=std::stoi(argv[1]);try{for(int d=1;d<=81;d++){uint64_t before=nodes;int v=search(0,0,0,d,-1,1);double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();std::cout<<"{\"depth\":"<<d<<",\"horizon_value\":"<<v<<",\"nodes\":"<<nodes<<",\"iteration_nodes\":"<<nodes-before<<",\"seconds\":"<<sec<<"}"<<std::endl;if(v!=0)break;}}catch(int){std::cout<<"{\"status\":\"UNKNOWN_TIMEOUT\",\"nodes\":"<<nodes<<"}"<<std::endl;}return 0;}
