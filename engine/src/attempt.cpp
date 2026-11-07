
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <thread>
#include <filesystem>
#include "solver/solver.h"
int main(int argc,char**argv){
 int seconds=argc>1?std::stoi(argv[1]):600;
 std::string opening=argc>2?argv[2]:"";
 Position p; for(char c:opening){int col=c-'1';if(p.is_game_over()||!p.is_move_valid(col))return 2;p.move(col);}
 Solver s; s.print_progress(); std::cout<<s.get_settings_string()<<"Opening: "<<opening<<" budget_seconds="<<seconds<<std::endl;
 std::mutex m; std::condition_variable cv; bool done=false; std::atomic<bool> expired=false;
 std::thread timer([&]{std::unique_lock<std::mutex> lk(m);auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(seconds);while(!done){cv.wait_for(lk,std::chrono::milliseconds(200),[&]{return done;});if(!done&&(std::chrono::steady_clock::now()>=deadline||std::filesystem::exists("stop.request"))){expired=true;s.cancel();break;}}});
 auto start=std::chrono::steady_clock::now();
 int v=s.solve(p);
 {std::lock_guard<std::mutex> lk(m);done=true;}cv.notify_one();timer.join();
 double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 std::cout<<"STATUS="<<(expired?"UNKNOWN_TIMEOUT":"SOLVED")<<" opening="<<opening<<" side_to_move_value="<<(expired?"null":std::to_string(v))<<" elapsed_seconds="<<elapsed<<std::endl;
 std::cout<<s.get_merged_stats().display_all_stats()<<std::endl;
 return expired?3:0;
}
