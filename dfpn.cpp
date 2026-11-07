// Depth-first proof-number search for the Boolean proposition: P1 can force a win.
#include <algorithm>
#include <bit>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <vector>
#include "engine/src/solver/position.h"
using PN=uint32_t;constexpr PN INF=1000000000;
struct N{PN p=1,d=1;};struct E{board key=0;N v{};};
std::vector<E> table(1<<22);uint64_t visits=0,expansions=0,hits=0,seeds=0;int seconds=300;auto start=std::chrono::steady_clock::now();
PN plus(PN a,PN b){return a>=INF-b?INF:a+b;}
size_t index(board k){uint64_t x=uint64_t(k)^uint64_t(k>>64)*0x9e3779b97f4a7c15ULL;x^=x>>30;x*=0xbf58476d1ce4e5b9ULL;x^=x>>27;x*=0x94d049bb133111ebULL;x^=x>>31;return x&(table.size()-1);}
N truth(bool yes){return yes?N{0,INF}:N{INF,0};}
N lookup(const Position&p){
 bool first=(p.num_moves()%2)==0;
 if(p.has_opponent_won())return truth(!first);
 if(p.has_player_won())return truth(first);
 if(p.is_draw())return truth(false);
 if(p.wins_this_move(p.find_player_threats()))return truth(first);
 board threats=p.find_opponent_threats(),safe=p.find_non_losing_moves(threats),ow=p.wins_this_move(threats);
 if(p.is_forced_loss_next_turn(ow,safe))return truth(!first);
 if(p.num_moves()>=35&&p.num_moves()<=73&&((81-p.num_moves())&1)==0){int bound=p.pairing_upper_bound();if(bound==-1)return truth(!first);if(bound==0&&first)return truth(false);}
 bool mirror;board k=p.hash(mirror);E&e=table[index(k)];if(e.key==k){hits++;return e.v;}return {};
}
bool infer_bound(bool first,int kind,int score,bool&known){known=true;if(kind==3&&score==0)return false;if((kind==1||kind==3)&&score==1)return first;if((kind==2||kind==3)&&score==-1)return !first;if(score==0&&((kind==2&&first)||(kind==1&&!first)))return false;known=false;return false;}
void load_bounds(const std::string&path){std::ifstream f(path);if(!f)throw std::runtime_error("missing seed bounds");std::string line;while(std::getline(f,line)){std::replace(line.begin(),line.end(),',',' ');std::istringstream in(line);uint64_t hi,lo,work;int move,kind,score;if(!(in>>hi>>lo>>move>>kind>>score>>work))throw std::runtime_error("malformed seed bound");board k=(board(hi)<<64)|lo;int ply=0;for(int c=0;c<9;c++)ply+=std::bit_width(unsigned((k>>(10*c))&1023))-1;bool known=false,yes=infer_bound((ply%2)==0,kind,score,known);if(known){table[index(k)]={k,truth(yes)};seeds++;}}}
void store(const Position&p,N n){bool mirror;board k=p.hash(mirror);table[index(k)]={k,n};}
N dfpn(Position&p,PN tp,PN td){
 if((++visits&4095)==0&&std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>seconds)throw 1;
 N known=lookup(p);if(known.p>=tp||known.d>=td||known.p==0||known.d==0)return known;
 bool is_or=(p.num_moves()%2)==0;board threats=p.find_opponent_threats();board non_losing=p.find_non_losing_moves(threats);
 struct C{int col;N n;int order;};std::array<C,9> children;int count=0;
 for(int c=0;c<9;c++)if(p.is_non_losing_move(non_losing,c)){
  board old=p.move(c);board t=p.find_opponent_threats();int order=__builtin_popcountll(uint64_t(t))+__builtin_popcountll(uint64_t(t>>64));N n=lookup(p);p.unmove(old);children[count++]={c,n,order};
 }
 if(!count)return truth(!is_or);
 expansions++;std::sort(children.begin(),children.begin()+count,[](C a,C b){return a.order>b.order;});
 auto aggregate=[&](){N n{is_or?INF:0,is_or?0:INF};for(int i=0;i<count;i++){if(is_or){n.p=std::min(n.p,children[i].n.p);n.d=plus(n.d,children[i].n.d);}else{n.p=plus(n.p,children[i].n.p);n.d=std::min(n.d,children[i].n.d);}}return n;};
 N current=aggregate();
 while(current.p<tp&&current.d<td&&current.p&&current.d){
  int best=0;for(int i=1;i<count;i++)if((is_or?children[i].n.p:children[i].n.d)<(is_or?children[best].n.p:children[best].n.d))best=i;
  PN second=INF;for(int i=0;i<count;i++)if(i!=best)second=std::min(second,is_or?children[i].n.p:children[i].n.d);
  PN cp,cd;
  if(is_or){cp=std::min(tp,plus(second,1));cd=td>=INF?INF:std::min(INF,td-current.d+children[best].n.d);}
  else{cp=tp>=INF?INF:std::min(INF,tp-current.p+children[best].n.p);cd=std::min(td,plus(second,1));}
  board old=p.move(children[best].col);try{children[best].n=dfpn(p,cp,cd);}catch(...){p.unmove(old);throw;}p.unmove(old);
  current=aggregate();store(p,current);
 }
 store(p,current);return current;
}
Position from_history(std::string s){Position p;for(char c:s){if(p.is_game_over()||c<'1'||c>'9'||!p.is_move_valid(c-'1'))throw std::runtime_error("illegal history");p.move(c-'1');}return p;}
int main(int argc,char**argv){
 if(argc>1&&std::string(argv[1])=="--validate"){
  int conversion_tests=0;for(bool first:{false,true})for(int kind:{1,2,3})for(int score:{-1,0,1}){bool known=false,yes=infer_bound(first,kind,score,known);int outcomes=0;for(int actual:{-1,0,1})if((kind==1&&actual>=score)||(kind==2&&actual<=score)||(kind==3&&actual==score)){bool proposition=actual!=0&&((actual==1)==first);outcomes|=proposition?2:1;if(known&&proposition!=yes)throw std::runtime_error("bound conversion unsound");}if((outcomes!=3)!=known)throw std::runtime_error("bound conversion incomplete");conversion_tests++;}
  seconds=120;if(argc>2)load_bounds(argv[2]);std::ifstream f("fixtures-9x9.jsonl");if(!f)return 2;std::string line;int tested=0;
  while(std::getline(f,line)){auto a=line.find(":\"");auto b=line.find('"',a+2);std::string hist=line.substr(a+2,b-a-2);auto v=line.find("side_to_move_value\"");int expected=std::stoi(line.substr(line.find(':',v)+1));Position p=from_history(hist);bool truth_expected=expected!=0&&((expected==1)==((p.num_moves()%2)==0));N n=dfpn(p,INF,INF);if((n.p==0)!=truth_expected||(!n.p&&!n.d)||(n.p!=0&&n.d!=0))throw std::runtime_error("DFPN disagreement");tested++;}
  std::cout<<"PASS independent_endgame_boolean_tests="<<tested<<" bound_conversion_tests="<<conversion_tests<<" seeded_records="<<seeds<<" visits="<<visits<<" expansions="<<expansions<<std::endl;return 0;
 }
 if(argc>1)seconds=std::stoi(argv[1]);std::string hist=argc>2?argv[2]:"5";Position p=from_history(hist);if(argc>3)load_bounds(argv[3]);
 try{N n=dfpn(p,INF,INF);std::cout<<"{\"status\":\""<<(n.p==0?"PROVED_P1_WIN":n.d==0?"PROVED_P1_CANNOT_FORCE_WIN":"UNKNOWN")<<"\",\"pn\":"<<n.p<<",\"dn\":"<<n.d;}
 catch(int){bool m;N n=lookup(p);std::cout<<"{\"status\":\"UNKNOWN_TIMEOUT\",\"pn\":"<<n.p<<",\"dn\":"<<n.d;}
 std::cout<<",\"opening\":\""<<hist<<"\",\"dfpn_visits\":"<<visits<<",\"expansions\":"<<expansions<<",\"table_hits\":"<<hits<<",\"wall_seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<"}"<<std::endl;
}
