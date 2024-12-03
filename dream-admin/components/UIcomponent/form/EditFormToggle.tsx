export default function EditFormToggle(props: any) {
    const { name, onChange, checked, children }: any = props;
    return (
        <label className="relative flex items-center cursor-pointer">
            <input type="checkbox" name={name} className="sr-only peer" onChange={onChange} checked={checked} />
            <div
                className="w-10 h-4 bg-gray-200 rounded-full peer 
            peer-checked:after:translate-x-full 
            after:absolute 
            after:top-1/2
            after:-translate-y-1/2
            after:left-[4px] 
            after:bg-white 
            after:border-gray-300 
            after:border 
            after:rounded-full 
            after:h-3 
            after:w-4 
            after:transition-all 
            peer-checked:bg-blue-500"
            ></div>
            <div className="ms-2 text-slate-400 peer-checked:text-slate-900">{children}</div>
        </label>
    );
}
//
